from booby.fields import *
from repose import validators
from repose.decoders import IdToLazyModelListDecoder
from repose.encoders import ModelToIdListEncoder
from repose.utilities import LazyList


class ManagedCollection(Collection):

    def __init__(self, model, *args, **kwargs):
        self.manager_class = kwargs.pop('manager', model.objects.__class__)
        super(ManagedCollection, self).__init__(model, *args, **kwargs)

    def _resolve(self, value):
        value = super(ManagedCollection, self)._resolve(value)
        return self._initialise_manager(value)

    def _initialise_manager(self, value):
        manager = self.manager_class()
        manager.results = value
        manager.contribute_to_class(self.model)
        return manager

class ManagedIdListCollection(ManagedCollection):
    """ Use for providing a managed collection upon a field which contains a
    list of model IDs.

    This does a little fancy footwork to ensure that the values
    are only loaded when accessed. This functionality is largely
    provided by LazyList
    """

    def __init__(self, model, *args, **kwargs):
        kwargs.setdefault('default', LazyList)
        super(ManagedIdListCollection, self).__init__(model, *args, **kwargs)
        self._initial_encoded_value = self._default(model)
        self.options['encoders'] = [ModelToIdListEncoder()]
        self.options['decoders'] = [IdToLazyModelListDecoder(model)]

    def _resolve(self, value):
        return self._initialise_manager(value)

    def decode(self, value):
        self._initial_encoded_value = value
        return super(ManagedIdListCollection, self).decode(value)

    def encode(self, value):
        if isinstance(value.results, list):
            import pdb; pdb.set_trace()
        if not value.results.has_changed():
            # Avoid loading the results if nothing has changed
            return self._initial_encoded_value
        else:
            return super(ManagedIdListCollection, self).encode(value)


class Dictionary(Field):
    """:class:`Field` subclass with `dict` validation."""

    def __init__(self, *args, **kwargs):
        super(Dictionary, self).__init__(validators.Dictionary(), *args, **kwargs)


class IsoDate(String):
    """ :class:`Field` subclass for ISO8601 dates.

    .. todo:: The :class:`IsoDate` field needs implementing
              Should parse ISO8601 strings into datetime objects and back again.

    """
    pass



