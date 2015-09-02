from repose.tests import User, Post, USER_DATA, TestCase


class ManagerTestCase(TestCase):

    def setUp(self):
        from repose.managers import Manager
        super(ManagerTestCase, self).setUp()
        self.manager = Manager()
        self.manager.contribute_client(self.client)
        self.manager.contribute_to_class(User)

    def test_get(self):
        self.client.add_response('GET', '/user/1', USER_DATA)
        user = self.manager.get(user_id=1)
        self.assertEqual(user.id, 1)
        self.assertEqual(user.name, 'Test User')

    def test_all(self):
        self.manager.contribute_to_class(User)
        self.client.add_response('GET', '/user', [USER_DATA])
        users = self.manager.all()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]['id'], 1)
