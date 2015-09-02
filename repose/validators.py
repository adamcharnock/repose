from booby.validators import *


class Range(Integer):
    """This validator forces fields values to be within a given range (inclusive)"""

    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    @nullable
    def validate(self, value):
        if self.max is not None:
            try:
                invalid = value > self.max
            except TypeError:
                raise errors.ValidationError('Invalid input data')

            if invalid:
                raise errors.ValidationError(
                    'Value {} exceeds maximum of {}'.format(value, self.max))

        if self.min is not None:
            try:
                invalid = value < self.min
            except TypeError:
                raise errors.ValidationError('Invalid input data')

            if invalid:
                raise errors.ValidationError(
                    'Value {} is below the minimum of {}'.format(value, self.min))


class Dictionary(Validator):

    @nullable
    def validate(self, value):
        if not isinstance(value, dict):
            raise errors.ValidationError('value must be a dictionary')
