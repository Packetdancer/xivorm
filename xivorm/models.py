from datetime import datetime
import asyncio
import threading
from . import global_thread, XivormThread
from .exceptions import XIVAPIServerError, XIVAPIThreadingException, XIVAPIException

XIVORM_MODEL_LIFETIME = datetime.timedelta(1800)

class XIVModelDataCache:

    last_refresh = datetime.utcfromtimestamp(0)
    _data_cache = {}
    _waiting_futures = {}
    _refreshing = False

    def __init__(self, lodestone_id=None, endpoint=None, parameters=None):
        if lodestone_id is None or endpoint is None:
            raise XIVAPIException("Object id and endpoint are not optional in a data cache.")

        self.lodestone_id = lodestone_id
        self.endpoint = endpoint
        self.parameters = parameters

    async def cache_data(self, response):
        if response.status == 200:
            self.last_refresh = datetime.utcnow()
            self._data_cache = await response.json()

            for k, v in self._data_cache:
                if k in self._waiting_futures:
                    futures = self._waiting_futures[k]
                    for wf in futures:
                        wf.set_result(v)
                    del self._waiting_futures[k]

            for k, v in self._waiting_futures:
                for wf in v:
                    wf.set_result(None)
                del self._waiting_futures[k]

            return

        status = "Unknown error has occurred."

        if response.status == 400:
            status = "Request was bad. Parameters may be incorrect."

        if response.status == 401:
            status = "Request was refused. API key may be invalid."

        if response.status == 404:
            status = "Resource not found."

        if response.status == 500:
            status = "Internal server error."

        if response.status == 503:
            status = "Service unavailable. (Lodestone maintenance?)"

        raise XIVAPIServerError(status, code=response.status)

    async def refresh(self):
        xt = threading.current_thread()
        if not isinstance(xt, XivormThread):
            raise XIVAPIThreadingException("Refresh called on a data cache from something other than Xivorm thread.")

        if self._refreshing:
            return

        self._refreshing = True
        full_url = f'{self.endpoint}/{self.lodestone_id}'
        async with xt.http.get(full_url, params=self.parameters) as response:
            self._refreshing = False
            await self.cache_data(response)

    def __getattr__(self, item):
        result = asyncio.get_event_loop().create_future()
        if datetime.utcnow() - self.last_refresh > XIVORM_MODEL_LIFETIME:
            futures = self._waiting_futures.get(item, [])
            futures.append(result)

            if not self._refreshing:
                xt = threading.current_thread()
                if not isinstance(xt, XivormThread):
                    raise XIVAPIThreadingException(
                        "Refresh called on a data cache from something other than Xivorm thread.")

                xt.schedule(self.refresh())

        if item in self._data_cache:
            result.set_result(self._data_cache[item])
        else:
            result.set_result(None)

        return result
