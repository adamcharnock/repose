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

    return model.Meta.endpoint.format(**values)


class LazyList(MutableSequence):
    """ Wraps a generate which from which data is only loaded when needed

    .. todo:: The :class:`LazyList` loading logic could be more intelligent
    """

    def __init__(self, generator, size):
        self._generator = generator
        self._size = size

    def set_parent_lazy(self, parent):
        self.parent = parent
        if self.is_loaded():
            self._set_parent()

    def is_loaded(self):
        return hasattr(self, '_values')

    def _set_parent(self):
        for v in self._values:
            v.contribute_parents(self.parent)

    def _load(self):
        if not self.is_loaded():
            self._values = list(self._generator)
            self._set_parent()

    def __len__(self):
        return self._size

    def __getitem__(self, index):
        self._load()
        return self._values[index]

    def __setitem__(self, index, value):
        self._load()
        self._values[index] = value

    def __delitem__(self, index):
        self._load()
        del self._values[index]

    def insert(self, i, x):
        self._load()
        self._values.insert(i, x)
