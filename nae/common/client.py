import requests


class HTTPClient(object):
    def __init__(self):
        self._session = None
        self.timeout = 86400

    def get_session(self):
        if not self._session:
            self._session = requests.Session()
        return self._session

    def request(self, url, method, **kwargs):
        kwargs.setdefault('headers', kwargs.get('headers', {}))
        kwargs['headers']['User-Agent'] = "API-CLIENT"
        kwargs['headers']['Accept'] = 'application/json'
        if 'data' in kwargs:
            kwargs['headers']['Content-Type'] = 'application/json'
        if self.timeout is not None:
            kwargs.setdefault('timeout', self.timeout)

        session = self.get_session()
        resp = session.request(method, url, **kwargs)

        return resp

    def get(self, url, **kwargs):
        return self.request(url, 'GET', **kwargs)

    def post(self, url, **kwargs):
        return self.request(url, 'POST', **kwargs)

    def put(self, url, **kwargs):
        return NotImplementedError()

    def delete(self, url, **kwargs):
        return self.request(url, 'DELETE', **kwargs)
