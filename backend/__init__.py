import logging
import typing

from quart import Quart
from quart_cors import cors

from .api import api
from .event_emitter import EventEmitter
from .session import SessionGC, SessionManager


def create_app():
    ALLOWED_ORIGINS: typing.Final[list[str]] = [
        "http://localhost:3000",
    ]

    logging.basicConfig(level=logging.DEBUG)

    app = Quart(__name__)
    app = cors(app, allow_origin=ALLOWED_ORIGINS)
    app.sm = SessionManager()
    app.ee = EventEmitter()

    session_gc = SessionGC(app.sm)

    @app.before_serving
    async def startup():
        session_gc.start()

    @app.after_serving
    async def shutdown():
        session_gc.stop()

    app.register_blueprint(api)

    return app


app = create_app()
