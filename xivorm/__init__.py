import asyncio
import threading
import aiohttp
from .exceptions import XIVAPIThreadingException, XIVAPIConfigurationError


api_key = "599ee498c3824597bebf1d48a4472faddf1e138e5e404f6283eb0f1091519e8e"

class XivormThread(threading.Thread):

    event_loop = None
    http = None
    api_key = None

    def __init__(self, api_key=None):
        super().__init__()
        if api_key is None:
            raise XIVAPIConfigurationError("You must provide an API key.")

        global_thread = self

    def run(self) -> None:
        self.event_loop = asyncio.get_event_loop()
        self.http = aiohttp.ClientSession(loop=self.event_loop)
        self.event_loop.run_forever()
        self.event_loop.close()

    def schedule(self, future):
        if not self.is_alive():
            raise XIVAPIThreadingException("The Xivorm thread has already been terminated.")

        if threading.current_thread() != self:
            raise XIVAPIThreadingException("Calling schedule from a thread other than the Xivorm thread is forbidden.")

        if not self.event_loop:
            raise XIVAPIThreadingException("No event loop is active.")

        self.event_loop.call_soon(future)

    def close_loop(self):
        self.event_loop.stop()
        self.event_loop.close()
