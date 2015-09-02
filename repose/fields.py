from booby.fields import *
from repose import validators
from repose.decoders import IdToLazyModelListDecoder
from repose.encoders import ModelToIdListEncoder


class ManagedCollection(Collection):

    def __init__(self, model, *args, **kwargs):
        self.manager = kwargs.pop('manager', model.objects.__class__())
        self.manager.contribute_to_class(model)
        super(ManagedCollection, self).__init__(model, *args, **kwargs)

    def _resolve(self, value):
        value = super(ManagedCollection, self)._resolve(value)
        self.manager.results = value
        return self.manager

    def encode(self, value):
        return super(ManagedCollection, self).encode(self.manager.results)

    def contribute_parent_to_models(self, parent):
        for resource in self.manager.all():
            resource.contribute_parents(parent)

    def __getattr__(self, name):
        return getattr(self.manager, name)


class ManagedIdListCollection(ManagedCollection):
    """ Use for providing a managed collection upon a field which contains a
    list of model IDs.

    This does a little fancy footwork to ensure that the values
    are only loaded when accessed. This functionality is largely
    provided by LazyList
    """

    def __init__(self, model, *args, **kwargs):
        super(ManagedIdListCollection, self).__init__(model, *args, **kwargs)
        self.options['encoders'] = [ModelToIdListEncoder()]
        self.options['decoders'] = [IdToLazyModelListDecoder(model)]

    def decode(self, value):
        self._initial_encoded_value = value
        return super(ManagedIdListCollection, self).decode(value)

    def encode(self, value):
        if not value.results.has_changed():
            # Avoid loading the results if nothing has changed
            return self._initial_encoded_value
        else:
            return super(ManagedIdListCollection, self).encode(value)

    def _resolve(self, value):
        self.manager.results = value
        return self.manager

    def contribute_parent_to_models(self, parent):
        self.manager.results.set_parent_lazy(parent)


class Dictionary(Field):
    """:class:`Field` subclass with `dict` validation."""

    def __init__(self, *args, **kwargs):
        super(Dictionary, self).__init__(validators.Dictionary(), *args, **kwargs)


class IsoDate(String):
    """ :class:`Field` subclass for ISO8601 dates.

    Details can be found in the
    `Philips Hue Documentation <http://www.developers.meethue.com/documentation/datatypes-and-time-patterns>`_.

    .. todo:: The :class:`IsoDate` field needs implementing
              Should parse ISO8601 strings into datetime objects and back again.

    """
    pass



