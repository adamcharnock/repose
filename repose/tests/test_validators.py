from booby.errors import ValidationError
from repose.tests import TestCase


class RangeValdiatorTestCase(TestCase):

    def test_min_max(self):
        from repose.validators import Range
        v = Range(min=10, max=20)
        v.validate(None)
        v.validate(10)
        v.validate(20)
        self.assertRaises(ValidationError, v.validate, -1)
        self.assertRaises(ValidationError, v.validate, 21)
        self.assertRaises(ValidationError, v.validate, 'abc')

    def test_min(self):
        from repose.validators import Range
        v = Range(min=10)
        v.validate(None)
        v.validate(10)
        v.validate(20)
        v.validate(10000)
        self.assertRaises(ValidationError, v.validate, -1)
        self.assertRaises(ValidationError, v.validate, 'abc')

    def test_max(self):
        from repose.validators import Range
        v = Range(max=20)
        v.validate(None)
        v.validate(-1)
        v.validate(10)
        v.validate(20)
        self.assertRaises(ValidationError, v.validate, 21)
        self.assertRaises(ValidationError, v.validate, 'abc')


class DictionaryValidatorTestCase(TestCase):

    def test_validate(self):
        from repose.validators import Dictionary
        v = Dictionary()
        v.validate(None)
        v.validate({})
        v.validate({'a': 123})
        self.assertRaises(ValidationError, v.validate, [])
        self.assertRaises(ValidationError, v.validate, 213)
        self.assertRaises(ValidationError, v.validate, 'abc')
