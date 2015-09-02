from repose.tests import User, Post, USER_DATA, TestCase


class MakeEndpointTestCase(TestCase):

    def test_make_endpoint(self):
        from repose.utilities import make_endpoint
        user = User(**USER_DATA)
        self.assertEqual(make_endpoint(user), '/user/1')

    def test_make_endpoint_child(self):
        from repose.utilities import make_endpoint
        user = User(**USER_DATA)
        post = Post(**USER_DATA['posts'][0])
        post.parent_resource = user
        self.assertEqual(make_endpoint(post), '/user/1/post/10')
