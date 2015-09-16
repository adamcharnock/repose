from repose.tests import TestCase, USER_DATA, User


class ManagedCollectionTestCase(TestCase):

    def test_encode(self):
        from repose.fields import ManagedCollection
        collection = ManagedCollection(User)
        collection.manager.results = [USER_DATA, USER_DATA]
        users = collection.all()
        self.assertEqual(len(users), 2)

    def test_different_refs(self):
        # Regression test for bug where ManagedCollection
        # would return the same objects for different
        # model instances
        from repose.fields import ManagedCollection
        user1 = User(**USER_DATA)
        user2 = User(**USER_DATA)

        self.assertIsNot(user1.posts.all()[0], user2.posts.all()[0])


class ManagedIdListCollectionTestCase(TestCase):

    def setUp(self):
        super(ManagedIdListCollectionTestCase, self).setUp()
        from repose.fields import ManagedIdListCollection
        collection = ManagedIdListCollection(User)
        collection.manager.contribute_api(self.api)
        self.collection = collection

    def test_decode(self):
        self.collection.manager.results = self.collection.decode([1,2,3])
        self.api.add_response('GET', '/user/1', USER_DATA)
        self.api.add_response('GET', '/user/2', USER_DATA)
        self.api.add_response('GET', '/user/3', USER_DATA)

        list(self.collection.all())
        self.assertEqual(len(self.api.requests), 3)

    def test_encode_no_change(self):
        data = [1,2,3]
        value = self.collection.decode(data)
        self.collection.manager.results = value

        # No change, so not api request should be done, we should
        # just get the exact data back that we put in
        self.assertIs(self.collection.encode(self.collection.manager), data)

    def test_encode_no_change_with_load(self):
        data = [1,2,3]
        value = self.collection.decode(data)
        self.collection.manager.results = value
        self.api.add_response('GET', '/user/1', USER_DATA)
        self.api.add_response('GET', '/user/2', USER_DATA)
        self.api.add_response('GET', '/user/3', USER_DATA)

        list(self.collection.all())
        # No change, so not api request should be done, we should
        # just get the exact data back that we put in
        self.assertIs(self.collection.encode(self.collection.manager), data)

    def test_encode_has_change(self):
        data = [1,2,3]
        value = self.collection.decode(data)
        self.collection.manager.results = value
        self.api.add_response('GET', '/user/1', USER_DATA)
        self.api.add_response('GET', '/user/2', USER_DATA)
        self.api.add_response('GET', '/user/3', USER_DATA)

        new_user = User(**USER_DATA)
        # TODO: This syntax doesn't look right at all. collection.append() would make more sense
        self.collection.all().append(new_user)
        list(self.collection.all())
        # No change, so not api request should be done, we should
        # just get the exact data back that we put in
        self.assertIsNot(self.collection.encode(self.collection.manager), data)


