from collections import MutableSequence


def make_endpoint(model):
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

    return model.Meta.endpoint.format(**values)


def get_values_from_endpoint(resource, endpoint_params):
    values = {}
    for k, v in resource._fields.items():
        field = v.options.get('from_endpoint')
        if field:
            values[field] = endpoint_params[field]
    return values


class LazyList(MutableSequence):
    """ Wraps a generate which from which data is only loaded when needed

    .. todo:: The :class:`LazyList` loading logic could be more intelligent
    """

    def __init__(self, generator, size):
        self._generator = generator
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
