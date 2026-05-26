import httpx
from config.enums import RequestMethod
import atexit

class Requestor:
    _client : httpx.Client | None =None
    
    def __init__(self):
        if Requestor._client is None:
            Requestor._client = httpx.Client(timeout=60)
            atexit.register(Requestor._client.close)

    def _sync_request(self, url:str=None, method:RequestMethod=RequestMethod.GET, headers=None, body=None):
        headers = {} if headers is None else headers
        response = Requestor._client.request(method=method, url=url, headers=headers, json=body)
        return response

    def _async_request(self):
        pass

    def request(self, url:str=None, method:RequestMethod=RequestMethod.GET, headers=None, body=None):
        response = self._sync_request(url, method, headers, body)
        return response