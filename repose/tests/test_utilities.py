from repose.tests import User, Post, USER_DATA, TestCase, POST_DATA


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


class LazyListTestCase(TestCase):

    def setUp(self):
        super(LazyListTestCase, self).setUp()
        from repose.utilities import LazyList
        l = [1,2,3,4]
        self.list = LazyList((x for x in l), size=len(l))

    def test_is_loaded(self):
        self.assertEqual(self.list.is_loaded(), False)
        self.list._load()
        self.assertEqual(self.list.is_loaded(), True)

    def test_len(self):
        self.assertEqual(len(self.list), 4)
        # Checking length should not trigger load
        self.assertEqual(self.list.is_loaded(), False)

    def test_get_item(self):
        self.assertEqual(self.list[0], 1)
        self.assertEqual(self.list[1], 2)
        self.assertEqual(self.list[2], 3)
        self.assertEqual(self.list[3], 4)
        self.assertEqual(self.list.is_loaded(), True)

    def test_set_item(self):
        self.list[0] = 9
        self.assertEqual(self.list[0], 9)
        self.assertEqual(self.list.is_loaded(), True)

    def test_del_item(self):
        del self.list[0]
        self.assertEqual(self.list.is_loaded(), True)
        self.assertEqual(len(self.list), 3)
        self.assertEqual(self.list, [2,3,4])

    def test_insert(self):
        self.list.insert(1, 9)
        self.assertEqual(self.list.is_loaded(), True)
        self.assertEqual(len(self.list), 5)
        self.assertEqual(self.list, [1, 9, 2,3,4])

    def test_set_parent_lazy(self):
        from repose.utilities import LazyList
        resources = [Post(**POST_DATA), Post(**POST_DATA)]
        lazy_list = LazyList((r for r in resources), size=2)
        parent = User(**USER_DATA)
        lazy_list.set_parent_lazy(parent)
        lazy_list._load()

        post1, post2 = resources
        self.assertEqual(post1.parent_resource.name, parent.name)
        self.assertEqual(post2.parent_resource.name, parent.name)
