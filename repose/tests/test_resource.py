from repose.tests import TestCase, USER_DATA, User


class ResourceTestCase(TestCase):

    def test_save(self):
        user = User(**USER_DATA)
        user.name = 'New Name'
        with self.api.assert_call('PUT',
                                     '/user/1',
                                     request_data=dict(name='New Name')):
            user.save()

