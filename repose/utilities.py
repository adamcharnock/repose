""" General utilities used within Repose.

*For the most part these can be ignored, their usage is
mainly for internal purposes.*
"""

from collections import MutableSequence


def make_endpoint(model):
    """Make an endpoint for a given model

    See the :class:`repose.resources.Resource.Meta` for a description
    of endpoint URL formatting.
    """
    parent = model.parent_resource
    models = [model]
    while parent:
        models.append(parent)
        parent = parent.parent_resource

    values = {}
    for inst in models:
        for k in inst._fields:
            values['{}_{}'.format(inst.__class__.__name__.lower(), k)] = getattr(inst, k)
            if inst is model:
                values[k] = getattr(inst, k)

    values.update(**model.get_endpoint_values())
    return model.Meta.endpoint.format(**values)


def get_values_from_endpoint(resource, endpoint_params):
    """Determine if any values in the endpoint parameters
    should be used to populate fields.

    An example of this would be resources which don't
    provide their own ID in the return data, and it must
    therefore come from the endpoint used to access the resource.
    In which case, you may define the resource's ID field as::

        id = fields.Integer(from_endpoint='id')

    Args:

        resource (:class:`repose.resources.Resource`):
            The class of the resource being populated
        endpoint_params (dict): All parameters available for formatting
            to the endpoint strings.

    """
    values = {}
    for k, v in resource._fields.items():
        field = v.options.get('from_endpoint')
        if field:
            values[field] = endpoint_params[field]
    return values


class LazyList(MutableSequence):
    """ Wraps a generator from which data is only loaded when needed.

    .. todo:: The :class:`LazyList` loading logic could be more intelligent

    .. todo:: Make the size parameter optional
    """

    def __init__(self, generator=None, size=0):
        """ Initialise the LazyList

        Args:

            generator (generator): The generator to be lazy loaded
            size (int): The size of the list to be loaded
        """
        self._generator = [] if generator is None else generator
        self._size = size
        self._changed = False

    def set_parent_lazy(self, parent):
        self.parent = parent
        if self.is_loaded():
            self._set_parent()

    def is_loaded(self):
        return hasattr(self, '_values')

    def has_changed(self):
        return self._changed

    def _set_parent(self):
        for v in self._values:
            if hasattr(v, 'contribute_parents'):
                v.contribute_parents(self.parent)

    def _load(self):
        if not self.is_loaded():
            self._values = list(self._generator)
            if hasattr(self, 'parent'):
                self._set_parent()

    def __len__(self):
        if self.is_loaded():
            return len(self._values)
        else:
            return self._size

    def __getitem__(self, index):
        self._load()
        return self._values[index]

    def __setitem__(self, index, value):
        self._load()
        self._values[index] = value
        self._changed = True

    def __delitem__(self, index):
        self._load()
        del self._values[index]
        self._changed = True

    def insert(self, i, x):
        self._load()
        self._values.insert(i, x)
        self._changed = True

    def __eq__(self, other):
        self._load()
        return self._values == list(other)
