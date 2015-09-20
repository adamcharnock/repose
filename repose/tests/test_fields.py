from repose.tests import TestCase, USER_DATA, User


class ManagedCollectionTestCase(TestCase):

    def setUp(self):
        super(ManagedCollectionTestCase, self).setUp()
        from repose import Resource, fields

        class Group(Resource):
            users = fields.ManagedCollection(User)

        self.resource = Group()
        self.resource.users.contribute_api(self.api)

    def test_encode(self):
        self.resource.users.results = [USER_DATA, USER_DATA]
        users = self.resource.users.all()
        self.assertEqual(len(users), 2)

    def test_different_refs(self):
        # Regression test for bug where ManagedCollection
        # would return the same objects for different
        # model instances
        user1 = User(**USER_DATA)
        user2 = User(**USER_DATA)

        self.assertIsNot(user1.posts.all()[0], user2.posts.all()[0])


class ManagedIdListCollectionTestCase(TestCase):

    def setUp(self):
        super(ManagedIdListCollectionTestCase, self).setUp()
        from repose import Resource, fields

        class Group(Resource):
            users = fields.ManagedIdListCollection(User)

        self.resource = Group()
        self.resource.users.contribute_api(self.api)

    def test_decode(self):
        data = [1,2,3]
        self.resource._update(self.resource.decode(raw=dict(users=data)))
        self.api.add_response('GET', '/user/1', USER_DATA)
        self.api.add_response('GET', '/user/2', USER_DATA)
        self.api.add_response('GET', '/user/3', USER_DATA)

        list(self.resource.users.all())
        self.assertEqual(len(self.api.requests), 3)

    def test_encode_no_change(self):
        data = [1,2,3]
        self.resource._update(self.resource.decode(raw=dict(users=data)))

        # No change, so no api request should be done, we should
        # just get the exact data back that we put in
        self.assertIs(self.resource.encode()['users'], data)

    def test_encode_no_change_with_load(self):
        data = [1,2,3]
        self.resource._update(self.resource.decode(raw=dict(users=data)))
        self.api.add_response('GET', '/user/1', USER_DATA)
        self.api.add_response('GET', '/user/2', USER_DATA)
        self.api.add_response('GET', '/user/3', USER_DATA)

        list(self.resource.users.all())
        # No change, so no api request should be done, we should
        # just get the exact data back that we put in
        self.assertIs(self.resource.encode()['users'], data)

    def test_encode_has_change(self):
        data = [1,2,3]
        self.resource._update(self.resource.decode(raw=dict(users=data)))
        self.api.add_response('GET', '/user/1', USER_DATA)
        self.api.add_response('GET', '/user/2', USER_DATA)
        self.api.add_response('GET', '/user/3', USER_DATA)

        new_user = User(**USER_DATA)
        # TODO: This syntax doesn't look right at all. users.append() would make more sense
        self.resource.users.all().append(new_user)
        list(self.resource.users.all())
        # Change, so api request is done and returned value is
        # NOT that of the initial data
        self.assertIsNot(self.resource.encode()['users'], data)


