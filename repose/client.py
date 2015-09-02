import requests

from repose import utilities


class Client(object):
    """The HTTP client used to access the remote API

    This can be extended and passed into your :class:`Api`
    instance at instantiation time.
    """

    def __init__(self, base_url):
        self.base_url = base_url

    def make_url(self, endpoint):
        return '{}/{}'.format(self.base_url.rstrip('/'), endpoint.lstrip('/'))

    def parse_response(self, response):
        response.raise_for_status()
        return response.json()

    def get(self, endpoint):
        r = requests.get(self.make_url(endpoint))
        return self.parse_response(r)

    def put(self, endpoint, json):
        r = requests.put(self.make_url(endpoint), json=json)
        return self.parse_response(r)

    def post(self, endpoint, json):
        r = requests.post(self.make_url(endpoint), json=json)
        return self.parse_response(r)
