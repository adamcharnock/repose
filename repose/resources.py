import weakref
from booby.models import ModelMeta, Model
import six
from repose.managers import Manager
from repose.utilities import make_endpoint, get_values_from_endpoint


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

    Attributes:

        parent_resource (list): A list of all parent resources to this one.
            Often useful in generating endpoints for child resources.
            Parent resources are stored as :func:`weakref.ref`

        api (Api): The API instance
    """

    class Meta:
        """ Override this class in child resources to provide
            configuration details.

            The endpoints listed here can include placeholders in the
            form ``{fieldname}``. If this resource is a child of another
            resource, the parent resource's fields may be accessed
            in the form ``{parentname_fieldname}}``, where ``parentname``
            is the lowercase class name.

            For example, a ``User`` resource may contain several ``Comment``
            resources. In which case the ``endpoint`` for the ``Comment``
            could be::

                /user/{user_id}/comments/{id}

            You could also expand the latter placeholder as follows::

                /user/{user_id}/comments/{comment_id}

            Attributes:

                endpoint (str): Endpoint URL for a single resource
                    (will be appended to the
                    API's :attr:`~repose.api.Api.base_url`)
                endpoint_list (str): Endpoint URL for listing resources
                    (will be appended to the
                    API's :attr:`~repose.api.Api.base_url`)
        """
        pass

    def __init__(self, **kwargs):
        """Initialise the resource with field values specified in ``*kwargs``

        Args:

            **kwargs: Fields and their (decoded) values

        """
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
    def contribute_api(cls, api):
        """Contribute the API backend to this resource and its managers.

        .. note:: Mainly for internal use
        """
        cls._api = api
        for manager in cls._managers:
            manager.contribute_api(api)

    def contribute_parents(self, parent=None):
        """Furnish this class with it's parent resources

        .. note:: Mainly for internal use
        """
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

    @property
    def api(self):
        try:
            return self._api
        except AttributeError:
            raise AttributeError(
                "Api not available on {}. Either you haven't instantiated "
                "an Api instance, or you haven't registered your resource "
                "with your Api instance.".format(self))

    def prepare_save(self, encoded):
        """Prepare the resource to be saved

        Will only return values which have changed

        Can be used as a hook with which to tweak data before
        sending back to the server. For example::

            def prepare_save(encoded):
                prepared = super(MyResource, self).prepare_save(encoded)
                prepared['extra_value'] = 'Something'
                return prepared

        Args:

            encoded (dict): The encoded resource data

        """
        prepared = {}
        for k, v in encoded.items():
            if k not in self._persisted_data or v != self._persisted_data[k]:
                prepared[k] = v
        return prepared

    def save(self):
        """Persist pending changes
        """
        endpoint = make_endpoint(self)
        encoded = self.encode()
        prepared_data = self.prepare_save(encoded)

        self.api.put(endpoint, prepared_data)
        self._persisted_data = encoded

    def get_endpoint_values(self):
        return {}

    def refresh(self):
        data = self.api.get(make_endpoint(self))
        decoded = self.__class__.decode(data)
        self._update(decoded)

    def as_dict(self):
        d = {}
        for field_name in self._fields.keys():
            d[field_name] = getattr(self, field_name)
        return d
