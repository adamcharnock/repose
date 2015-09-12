"""
Decoders are used be fields to decode incoming data from
the API into a form usable in Python.

Those listed here are typically used by the :mod:`~repose.fields`
module. Unless you are creating your own field, you can probably
focus your attention there.

This is the inverse operation to that of :mod:`~repose.encoders`.
"""

from booby.decoders import *
from booby.helpers import nullable
from repose.utilities import LazyList


class IdToLazyModelListDecoder(Decoder):
    """ Decode a list of resource IDs into a lazily loaded list of
    :class:`~repose.resources.Resource` objects
    """

    def __init__(self, resource):
        """ Initialise the decoder

        Args:

            resource (Resource): The Resource class (*not an instance*) to which the
                IDs listed relate.
        """
        self._resource = resource

    @nullable
    def decode(self, value):
        """ Decode the value into a :class:`LazyList`.

        .. note:: This assumes the destination
            :class:`~repose.resources.Resource` has an ID field
            and that the endpoint is in the form ``/myresource/{myresource_id}``

        .. todo:: Consider refactoring out these assumptions
        """
        url_key = '{}_id'.format(self._resource.__name__.lower())
        gen = (self._resource.objects.get(**{url_key: id}) for id in value)
        return LazyList(generator=gen, size=len(value))

