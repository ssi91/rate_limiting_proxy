import asyncio


class RLQ(asyncio.Queue):
    RPP = 5
    PERIOD = 1

    def __init__(self):
        super().__init__(self.RPP)

    def _init(self, maxsize):
        super()._init(maxsize)
        for i in range(maxsize):
            self._queue.append(1)
        self.task = asyncio.ensure_future(self.dispatcher(maxsize))

    async def dispatcher(self, maxsize):
        while True:
            await asyncio.sleep(self.PERIOD)
            for i in range(maxsize - self.qsize()):
                self.put_nowait(1)

    def cancel(self):
        self.cancel()


def rate_limit_middleware(q):
    async def rate_limit_dec(app, func):
        async def wrapper(*args, **kwargs):
            await q.get()
            return await func(*args, **kwargs)

        return wrapper

    return rate_limit_dec
