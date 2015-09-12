"""
Decoders are used be fields to encode Python values into a form
consumable by the API.

Those listed here are typically used by the :mod:`~repose.fields`
module. Unless you are creating your own field, you can probably
focus your attention there.

This is the inverse operation to that of :mod:`~repose.decoders`.
"""

from booby.encoders import *
from booby.helpers import nullable


class ModelToIdListEncoder(Encoder):
    """ Encode a list of :class:`~repose.resources.Resource` instances
    into a list of resource IDs.
    """

    @nullable
    def encode(self, value):
        """ Initialise the encoder

        Args:

            value (list[Resource]):
                A list of :class:`~repose.resources.Resource`
                instances to be encoded
        """
        return [m.id for m in value]
