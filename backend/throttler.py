import asyncio
from datetime import datetime, timedelta


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
