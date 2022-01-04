import asyncio
import logging
import typing
from contextlib import contextmanager
from logging import Logger


class EventEmitter:
    logger: Logger = logging.getLogger("EventEmitter")
    channels: dict[str, set[asyncio.Queue]]

    def __init__(self):
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
