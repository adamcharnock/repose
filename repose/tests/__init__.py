from requests.models import Response
from repose import fields, utilities
from repose.api import Api
from repose.client import Client
from repose.resources import Resource


class UnexpectedRequest(Exception): pass


class DummyResponse(object):

    def __init__(self, json):
        self._json = json

    def json(self):
        return self._json


class TestClient(Client):
    responses = {}

    def add_response(self, method, endpoint, data):
        response = DummyResponse(data)
        self.responses.update(**{
            (method.upper(), endpoint.rstrip('/')): response
        })

    def _request(self, method, endpoint):
        method = method.upper()
        endpoint = endpoint.rstrip('/')
        try:
            response = self.responses[method, endpoint]
        except:
            raise UnexpectedRequest('{} {}'.format(method, endpoint))

        return utilities.parse_response(response)

    def get(self, endpoint):
        return self._request('GET', endpoint)

    def put(self, endpoint, json):
        return self._request('PUT', endpoint)

    def post(self, endpoint, json):
        return self._request('POST', endpoint)


class Post(Resource):
    id = fields.Integer()
    content = fields.String()

    class Meta:
        endpoint = '/user/{user_id}/post/{post_id}'
        endpoint_list = '/user/{user_id}/post'


class User(Resource):
    id = fields.Integer()
    name = fields.String()
    posts = fields.ManagedCollection(Post)

    class Meta:
        endpoint = '/user/{user_id}'
        endpoint_list = '/user'


class TestApi(Api):
    resources = [User]
    client_class = TestClient
    base_url = '/test-api/'


USER_DATA = {
    'id': 1,
    'name': 'Test User',
    'posts': [
        {
            'id': 10,
            'content': 'First Comment'
        },{
            'id': 11,
            'content': 'Second Comment'
        },
    ]
}
