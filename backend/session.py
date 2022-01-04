import asyncio
import logging
import uuid
from asyncio import Task
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from logging import Logger
from typing import Optional
from uuid import UUID

from .tic_tac_toe import Sign, TicTacToe, next_turn


@dataclass
class Player:
    name: str
    sign: Sign


class SessionException(Exception):
    pass


class PlayerAlreadyJoinedException(SessionException):
    def __init__(self, p_id: str):
        super().__init__(f"The player {p_id!r} has already joined the session")


class AllPlayersAlreadyJoinedException(SessionException):
    def __init__(self):
        super().__init__("All players have already joined the session")


class Session:
    SESSION_TIMEOUT: timedelta = timedelta(minutes=10)

    logger: Logger = logging.getLogger("Session")

    id: UUID
    game: TicTacToe
    active_players: set[str]
    players: dict[str, Player]
    released_at: datetime
    sign: Sign

    def __init__(self, field: int):
        self.id = uuid.uuid4()
        self.game = TicTacToe(field)
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
            self.logger.debug(f"Adding {name!r}")
            self.active_players.add(name)
        else:
            self.logger.debug(f"Removing {name!r}")
            self.active_players.remove(name)

    def get_players_sign(self, name: str) -> Sign:
        return self.players[name].sign

    def is_players_turn(self, name: str) -> bool:
        return self.game.turn == self.get_players_sign(name)


class SessionNotFoundError(SessionException):
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

    def create(self, field: int) -> Session:
        session = Session(field)
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
    sm: SessionManager
    gc_task: Optional[Task]
    gc_interval: timedelta
    logger: Logger = logging.getLogger("SessionGC")

    def __init__(
        self, sm: SessionManager, gc_interval: timedelta = timedelta(minutes=5)
    ):
        self.sm = sm
        self.gc_task = None
        self.gc_interval = gc_interval

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
            res = self.sm.gc()
            self.logger.info(res)
