from contextlib import contextmanager
from unittest import TestCase as BaseTestCase
from repose import fields, utilities
from repose.api import Api
from repose.client import Client
from repose.managers import Manager
from repose.resources import Resource


class UnexpectedRequest(Exception): pass


class TestCase(BaseTestCase):

    def setUp(self):
        from repose.tests import TestApi
        self.api = TestApi()
        self.client = self.api.client


class DummyResponse(object):

    def __init__(self, json):
        self._json = json

    def json(self):
        return self._json


class TestClient(Client):
    responses = {}
    requests = []

    def add_response(self, method, endpoint, data):
        response = DummyResponse(data)
        key = (method.upper(), endpoint.rstrip('/'))
        self.responses[key] =response

    def _request(self, method, endpoint, json=None):
        method = method.upper()
        endpoint = endpoint.rstrip('/')
        try:
            response = self.responses[method, endpoint]
            self.requests.append((method, endpoint, json, True))
        except:
            self.requests.append((method, endpoint, json, False))
            raise UnexpectedRequest('{} {}'.format(method, endpoint))

        return self.parse_response(response.json())

    def get(self, endpoint):
        return self._request('GET', endpoint)

    def put(self, endpoint, json):
        return self._request('PUT', endpoint, json)

    def post(self, endpoint, json):
        return self._request('POST', endpoint, json)

    @contextmanager
    def assert_call(self, method, endpoint, request_data=None, response_data=None):
        """ Assert a call is made

        :param method: string The HTTP method expected (get, put, post, delete)
        :param endpoint: string The HTTP endpoint expected (e.g. `/user/1`)
        :param request_data: dict Expected contents of the request body
        :param response_data: dict The response body the client should return
        """
        self.add_response(method.upper(), endpoint, response_data)
        initial_len = len(self.requests)
        yield

        assert len(self.requests) > initial_len, "No request was made"
        assert len(self.requests) == initial_len + 1, "Too many requests were made"
        actual_method, actual_endpoint, actual_request_data, actual_response_data = \
            self.requests[initial_len]
        assert actual_method == method, "Methods did not match"
        assert actual_endpoint == endpoint, "Endpoints did not match"
        if request_data is not None:
            assert actual_request_data == request_data, "Request data did not match. " \
                                                        "{} != {}"\
                                                        .format(request_data, actual_request_data)



class Post(Resource):
    id = fields.Integer()
    content = fields.String()

    class Meta:
        endpoint = '/user/{user_id}/post/{post_id}'
        endpoint_list = '/user/{user_id}/post'


class Profile(Resource):
    email = fields.String()
    age = fields.Integer()


class User(Resource):
    id = fields.Integer()
    name = fields.String()
    posts = fields.ManagedCollection(Post)
    profile = fields.Embedded(Profile)

    objects = Manager()
    with_posts = Manager(filter=lambda u: u.posts.count() > 0)

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
    'profile': {
        'email': 'test@example.com',
        'age': 42,
    },
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


POST_DATA = {
    'id': 1,
    'content': 'Hello there',
}
