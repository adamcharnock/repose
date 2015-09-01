from unittest.case import TestCase
from repose.tests import User, USER_DATA


class MakeEndpointTestCase(TestCase):

    def setUp(self):
        from repose.tests import TestApi
        self.api = TestApi()
        self.client = self.api.client

    def test_make_endpoint(self):
        from repose.utilities import make_endpoint
        user = User(**USER_DATA)
        self.assertEqual(make_endpoint(user), '/user/1')

    def test_make_endpoint_child(self):
        from repose.utilities import make_endpoint
        user = User(**USER_DATA)
        post = user.posts.all()[0]
        self.assertEqual(make_endpoint(post), '/user/1/post/10')
