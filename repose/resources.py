import weakref
from booby.models import ModelMeta, Model
import six
from repose.managers import Manager
from repose.utilities import make_endpoint


class ResourceMetaclass(ModelMeta):
    """ Meta class for setting up Resource classes
    """

    def __new__(cls, clsname, bases, dct):
        resource = super(ResourceMetaclass, cls).__new__(cls, clsname, bases, dct)
        cls.setup_managers(resource, dct)
        return resource

    @classmethod
    def setup_managers(cls, resource, dct):
        """Setup the managers on a resource

        Pass a reference to the resource class to all attached managers,
        and create a default manager if none are explicitly defined
        """
        has_custom_manager = False
        managers = []
        for k, v in dct.items():
            if isinstance(v, Manager):
                v.contribute_to_class(resource)
                has_custom_manager = True
                managers.append(v)

        # If we don't have a custom manager, then add the
        # default manager
        if not has_custom_manager:
            manager = Manager()
            manager.contribute_to_class(resource)
            resource.objects = manager
            managers.append(manager)

        resource._managers = managers


class Resource(six.with_metaclass(ResourceMetaclass, Model)):
    """ Representation of an API resource

    :ivar parent_resource:
        A list of all parent resources to this one. Often useful in
        generating endpoints for child resources. Parent resources are
        stored as :py:func:`weakref.ref`
    """

    class Meta:
        """ Override this class in child resources to provide
            configuration details.
        """
        pass

    def __init__(self, **kwargs):
        self.parent_resource = []
        # Only use fields which have been specified on the resource
        data = {}
        for f in self._fields.keys():
            # Get from kwargs is available, otherwise
            # get the default value from the current attribute value
            data[f] = kwargs.get(f) or getattr(self, f)

        super(Resource, self).__init__(**data)
        self.contribute_parents()
        self._persisted_data = self.encode()


    @classmethod
    def contribute_client(cls, client):
        """Contribute the API client to this resource and its managers"""
        cls.client = client
        for manager in cls._managers:
            manager.contribute_client(client)

    def contribute_parents(self, parent=None):
        """Furnish this class with it's parent resources"""
        if parent:
            parent = weakref.proxy(parent)
        self.parent_resource = parent

        for k, v in self._fields.items():
            if hasattr(v, 'contribute_parent_to_models'):
                # This is a ManagedCollection of some sort, so
                # let it handle contributing to its models
                v.contribute_parent_to_models(parent=self)
            elif hasattr(getattr(self, k), 'contribute_parents'):
                # This is an Embedded field of some sort. The
                # value attached to the resource will be another
                # resource, so directly contribute to its parents
                getattr(self, k).contribute_parents(parent=self)

    def prepare_save(self, encoded):
        """Prepare the resource to be saved

        Will only return values which have changed

        Can be used as a hook with which to tweak data before
        sending back to the server. For example::

            def prepare_save(encoded):
                prepared = super(MyResource, self).prepare_save(encoded)
                prepared['extra_value'] = 'Something'
                return prepared

        :param encoded: dict The encoded resource data

        """
        for k, v in encoded.items():
            if k in self._persisted_data and v == self._persisted_data[k]:
                encoded.pop(k)
        return encoded

    def save(self):
        """Persist pending changes
        """
        endpoint = make_endpoint(self)
        encoded = self.encode()
        prepared_data = self.prepare_save(encoded.copy())

        self.client.put(endpoint, prepared_data)
        self._persisted_data = encoded
