from booby.decoders import *
from booby.helpers import nullable
from repose.utilities import LazyList


class IdToLazyModelListDecoder(Decoder):

    def __init__(self, model):
        self._model = model

    @nullable
    def decode(self, value):
        url_key = '{}_id'.format(self._model.__name__.lower())
        gen = (self._model.objects.get(**{url_key: id}) for id in value)
        return LazyList(generator=gen, size=len(value))

