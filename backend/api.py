import asyncio
import re
import typing
from datetime import timedelta
from http import HTTPStatus
from json import JSONDecodeError
from uuid import UUID

from pydantic import BaseModel, ValidationError, parse_raw_as
from quart import Blueprint, current_app, request, websocket

from .session import SessionException
from .throttler import Throttler
from .tic_tac_toe import GameplayError, NotPlayersTurnError


class CreateSessionRequest(BaseModel):
    field: int


class GameMoveRequest(BaseModel):
    row: int
    col: int


api = Blueprint("Session API", __name__)


@api.post("/sessions")
async def create_session():
    try:
        payload = parse_raw_as(CreateSessionRequest, await request.data)
    except JSONDecodeError:
        return {"error": "Invalid JSON structure"}, HTTPStatus.BAD_REQUEST
    except ValidationError:
        return {"error": "Invalid body"}, HTTPStatus.BAD_REQUEST

    session = current_app.sm.create(payload.field)

    return {"id": str(session.id)}


player_name_regex: typing.Final[re.Pattern] = re.compile(r"\w{1,10}")


async def with_timeout(
    coro: typing.Coroutine, timeout: timedelta = timedelta(minutes=1)
):
    return await asyncio.wait_for(coro, float(timeout.seconds))


@api.websocket("/sessions/<uuid:s_id>/players/<p_id>/join")
async def join_session(s_id: UUID, p_id: str):
    SESSION_EVENT: typing.Final[str] = str(s_id)

    async def send_json(payload):
        await with_timeout(websocket.send_json(payload))

    async def send_error(e: Exception):
        await send_json({"error": str(e)})

    async def recv_json():
        return await with_timeout(websocket.receive_json())

    try:
        session = current_app.sm.get(s_id)

        if not player_name_regex.match(p_id):
            await send_json({"error": "Invalid player name format"})
            return

        with session.activate_player(p_id), current_app.ee.subscription(
            SESSION_EVENT
        ) as chan:
            current_app.ee.emit(SESSION_EVENT)

            async def sender():
                async for _ in chan:
                    try:
                        current_app.logger.debug(f"Sending data to player {p_id!r}")
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
                        current_app.ee.emit(SESSION_EVENT)
                    except GameplayError as e:
                        await send_error(e)

            await asyncio.gather(sender(), receiver())

    except SessionException as e:
        await send_error(e)
    except Exception as e:
        current_app.logger.error(e)
        current_app.ee.emit(SESSION_EVENT)
        await websocket.close(code=1001)
