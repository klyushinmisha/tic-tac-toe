import asyncio
import enum
import logging
import typing
import uuid
from asyncio import Task
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from logging import Logger
from typing import Optional
from uuid import UUID

import regex
from pydantic import BaseModel
from quart import Quart, websocket
from quart_cors import cors

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Sign(enum.Enum):
    NONE = None
    NOUGHT = "o"
    CROSS = "x"


def next_turn(turn: Sign) -> Sign:
    if turn == Sign.NOUGHT:
        return Sign.CROSS
    if turn == Sign.CROSS:
        return Sign.NOUGHT
    raise ValueError(f"Unexpected turn value: {turn!r}")


class GameException(Exception):
    pass


class GameplayException(Exception):
    pass


class UsedFieldError(GameplayException):
    def __init__(self, row: int, col: int):
        super().__init__(f"Field (row={row};col={col}) is used")


class NotPlayersTurnError(GameplayException):
    def __init__(self):
        super().__init__("Wait for second player's move")


class TicTacToe:
    board: list[list[Sign]]
    turn: Sign

    def __init__(self, n=3):
        self.board = [[Sign.NONE for _ in range(n)] for _ in range(n)]
        self.turn = Sign.CROSS

    def move(self, row: int, col: int):
        if self.board[row][col] != Sign.NONE:
            raise UsedFieldError(row, col)
        self.board[row][col] = self.turn
        self.turn = next_turn(self.turn)

    @property
    def state(self) -> list[list[Optional[str]]]:
        return [[cell.value for cell in row] for row in self.board]

    @property
    def game_over(self) -> bool:
        signed = sum(sum(1 for cell in row if cell != Sign.NONE) for row in self.board)
        n = len(self.board)
        return self.winner != Sign.NONE or signed == n ** 2

    @property
    def winner(self) -> Sign:
        n = len(self.board)

        # rows
        for i in range(n):
            p1, p2 = 0, 0
            for j in range(n):
                if self.board[i][j] == Sign.NOUGHT:
                    p1 += 1
                if self.board[i][j] == Sign.CROSS:
                    p2 += 1
            if p1 == n:
                return Sign.NOUGHT
            if p2 == n:
                return Sign.CROSS

        # cols
        for i in range(n):
            p1, p2 = 0, 0
            for j in range(n):
                if self.board[j][i] == Sign.NOUGHT:
                    p1 += 1
                if self.board[j][i] == Sign.CROSS:
                    p2 += 1
            if p1 == n:
                return Sign.NOUGHT
            if p2 == n:
                return Sign.CROSS

        # diagonal 1
        p1, p2 = 0, 0
        for i in range(n):
            if self.board[i][i] == Sign.NOUGHT:
                p1 += 1
            if self.board[i][i] == Sign.CROSS:
                p2 += 1
        if p1 == n:
            return Sign.NOUGHT
        if p2 == n:
            return Sign.CROSS

        # diagonal 2
        p1, p2 = 0, 0
        for i in range(n):
            if self.board[n - i - 1][i] == Sign.NOUGHT:
                p1 += 1
            if self.board[n - i - 1][i] == Sign.CROSS:
                p2 += 1
        if p1 == n:
            return Sign.NOUGHT
        if p2 == n:
            return Sign.CROSS

        return Sign.NONE


@dataclass
class Player:
    name: str
    sign: Sign


class PlayerAlreadyJoinedException(GameException):
    def __init__(self, p_id: str):
        super().__init__(f"The player {p_id!r} has already joined the session")


class AllPlayersAlreadyJoinedException(GameException):
    def __init__(self):
        super().__init__("All players have already joined the session")


class Session:
    SESSION_TIMEOUT: timedelta = timedelta(minutes=1)

    id: UUID
    game: TicTacToe
    active_players: set[str]
    players: dict[str, Player]
    released_at: datetime
    sign: Sign

    def __init__(self):
        self.id = uuid.uuid4()
        self.game = TicTacToe()
        self.active_players = set()
        self.players = {}
        self.released_at = datetime.now()
        self.sign = Sign.CROSS

    @property
    def winner(self) -> Optional[str]:
        win = [p.name for p in self.players.values() if p.sign == self.game.winner]
        if len(win) == 1:
            return win[0]
        return None

    @property
    def is_dead(self) -> bool:
        return (
            len(self.active_players) == 0
            and self.released_at + self.SESSION_TIMEOUT < datetime.now()
        )

    @contextmanager
    def activate_player(self, name: str):
        self.add_player(name)
        self.mark_player(name, online=True)
        try:
            yield
        finally:
            self.mark_player(name, online=False)
            self.released_at = datetime.now()

    def add_player(self, name: str):
        ps = set(self.players)
        if name not in ps:
            if len(ps) == 2:
                raise AllPlayersAlreadyJoinedException()
            p = Player(name, self.sign)
            self.sign = next_turn(self.sign)
            self.players[p.name] = p

    def mark_player(self, name: str, online: Optional[bool] = False):
        if online:
            if name in self.active_players:
                raise PlayerAlreadyJoinedException(name)
            logger.debug(f"Adding {name!r}")
            self.active_players.add(name)
        else:
            logger.debug(f"Removing {name!r}")
            self.active_players.remove(name)

    def get_players_sign(self, name: str) -> Sign:
        return self.players[name].sign

    def is_players_turn(self, name: str) -> bool:
        return self.game.turn == self.get_players_sign(name)


class SessionNotFoundError(GameException):
    def __init__(self, s_id: UUID):
        super().__init__(f"Session {s_id} is not found")


@dataclass
class GCResult:
    sessions: list[uuid.UUID] = field(default_factory=list)

    def __str__(self):
        total = len(self.sessions)
        if total == 0:
            return "No dead sessions have been found"
        str_sessions = "".join(f"  * {s_id}\n" for s_id in self.sessions)
        return f"""Dead sessions:\n{str_sessions}Total: {total}"""


class SessionManager:
    sessions: dict[UUID, Session]

    def __init__(self):
        self.sessions = {}

    def create(self) -> Session:
        session = Session()
        self.sessions[session.id] = session
        return session

    def get(self, s_id: UUID) -> Session:
        try:
            return self.sessions[s_id]
        except KeyError:
            raise SessionNotFoundError(s_id)

    def delete(self, s_id: UUID):
        self.sessions.pop(s_id)

    def gc(self) -> GCResult:
        result = GCResult()
        gc_ids = set()
        for session in self.sessions.values():
            if session.is_dead:
                gc_ids.add(session.id)
        for s_id in gc_ids:
            self.delete(s_id)
            result.sessions.append(s_id)
        return result


class SessionGC:
    gc_task: Optional[Task]
    gc_interval: timedelta
    logger: Logger = logging.getLogger("SessionGC")

    def __init__(self, gc_interval: timedelta = timedelta(seconds=10)):
        self.gc_task = None
        self.gc_interval = gc_interval
        self.logger.setLevel(logging.INFO)

    def start(self):
        self.gc_task = asyncio.create_task(self.run_gc())

    def stop(self):
        if self.gc_task is not None:
            self.gc_task.cancel()
            self.gc_task = None

    async def run_gc(self):
        next_gc = datetime.now() + self.gc_interval
        while True:
            sleep_dur = max(next_gc - datetime.now(), timedelta())
            self.logger.debug(f"Sleeping for {sleep_dur}")
            await asyncio.sleep(sleep_dur.seconds)
            self.logger.debug(f"Awake. Running a GC cycle")
            next_gc = datetime.now() + self.gc_interval
            res = sm.gc()
            self.logger.info(res)


sm = SessionManager()
session_gc = SessionGC()

ALLOWED_ORIGINS: typing.Final[list[str]] = [
    "http://localhost:3000",
]

app = Quart(__name__)
app = cors(app, allow_origin=ALLOWED_ORIGINS)


@app.before_serving
async def startup():
    session_gc.start()


@app.after_serving
async def shutdown():
    session_gc.stop()


@app.post("/sessions")
async def create_session():
    session = sm.create()

    return {"id": str(session.id)}


class GameMoveRequest(BaseModel):
    row: int
    col: int


async def with_timeout(
    coro: typing.Coroutine, timeout: timedelta = timedelta(minutes=10)
):
    return await asyncio.wait_for(coro, float(timeout.seconds))


class EventEmitter:
    logger: Logger = logging.getLogger("EventEmitter")
    channels: dict[str, set[asyncio.Queue]]

    def __init__(self):
        self.logger.setLevel(logging.DEBUG)
        self.channels = {}

    @contextmanager
    def subscription(self, e: str):
        if e not in self.channels:
            self.channels[e] = set()
        chan = asyncio.Queue()
        self.channels[e].add(chan)
        self.logger.debug(f"Subscribed on {e!r}")

        async def chan_iter():
            while True:
                yield await chan.get()

        try:
            yield chan_iter()
        finally:
            self.logger.debug(f"Unsubscribed from {e!r}")
            self.channels[e].remove(chan)
            if len(self.channels[e]) == 0:
                self.channels.pop(e)

    def emit(self, e: str, data: typing.Any = None):
        for chan in self.channels.get(e, set()):
            chan.put_nowait(data)
        self.logger.debug(f"Event {e!r} was emitted")


ee = EventEmitter()


class Throttler:
    next: datetime
    throttle_dt: timedelta

    def __init__(self, throttle_dt: timedelta = timedelta(milliseconds=100)):
        self.next = datetime.now()
        self.throttle_dt = throttle_dt

    async def throttle(self):
        sleep_dt = max(self.next - datetime.now(), timedelta())
        await asyncio.sleep(sleep_dt.seconds)
        self.next = datetime.now() + self.throttle_dt


player_name_regex: typing.Final[regex.Regex] = regex.compile(r"\w{1,10}")


@app.websocket("/sessions/<uuid:s_id>/players/<p_id>/join")
async def join_session(s_id: UUID, p_id: str):
    SESSION_EVENT: typing.Final[str] = str(s_id)

    async def send_json(payload):
        await with_timeout(websocket.send_json(payload))

    async def send_error(e: Exception):
        await send_json(str(e))

    async def recv_json():
        return await with_timeout(websocket.receive_json())

    try:
        session = sm.get(s_id)

        if not player_name_regex.match(p_id):
            await send_json({"error": "Invalid player name format"})
            return

        with session.activate_player(p_id), ee.subscription(SESSION_EVENT) as chan:
            ee.emit(SESSION_EVENT)

            async def sender():
                async for _ in chan:
                    try:
                        logger.debug(f"Sending data to player {p_id!r}")
                        await send_json(
                            {
                                "you": p_id,
                                "state": session.game.state,
                                "your_turn": session.is_players_turn(p_id),
                                "your_sign": session.get_players_sign(p_id).value,
                                "game_over": session.game.game_over,
                                "winner": session.game.winner.value,
                                "active_players": [
                                    {"name": p.name, "sign": p.sign.value}
                                    for p in session.players.values()
                                    if p.name in session.active_players
                                ],
                            }
                        )
                    except asyncio.TimeoutError:
                        await websocket.close(code=1001)

            async def receiver():
                throttler = Throttler()
                while True:
                    try:
                        await throttler.throttle()
                        payload = await recv_json()
                        if not session.is_players_turn(p_id):
                            raise NotPlayersTurnError()
                        move = GameMoveRequest(**payload)
                        session.game.move(move.row, move.col)
                        ee.emit(SESSION_EVENT)
                    except GameplayException as e:
                        await send_error(e)

            await asyncio.gather(sender(), receiver())

    except GameException as e:
        await send_error(e)
    except Exception as e:
        logger.error(e)
        ee.emit(SESSION_EVENT)
        await websocket.close(code=1001)
