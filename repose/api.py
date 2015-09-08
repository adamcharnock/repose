from repose.apibackend import ApiBackend


class Api(object):
    """ A top-level API representation

    Initialising an ``Api`` instance is a necessary step as
    doing so will furnish all registered Resources (and their Managers)
    with access to the API backend.

    For example::

        my_api = Api(base_url='http://example.com/api/v1')
        my_api.register_resource(User)
        my_api.register_resource(Comment)
        my_api.register_resource(Page)

    The same can be achieved by implementing a child class. This also
    gives the additional flexibility of being able to add more complex
    logic by overriding existing methods. For example::

        class MyApi(Api):
            # Alternative way to provide base_url and resources
            base_url = '/api/v1'
            resources = [User, Comment, Page]

            # Additionally, customise the base URL generation
            def get_base_url(self):
                return 'http://{host}/api/{account}'.format(
                    host=self.host,
                    account=self.account,
                )

        my_api = MyApi(host='myhost.com', account='my-account')

    .. note: All options passed to the Api's constructor will become
             available as instance variables. See the able example and
             the use of ``account``.
    """

    backend_class = ApiBackend
    base_url = None
    resources = []

    def __init__(self, **options):
        """ Initialise the Api

        Pass options in to customise instance variables. For example::

            my_api = Api(base_url='http://example.com/api/v1')

        :param options: All options specified will will become
                        available as instance variables.
        """
        for k, v in options.items():
            setattr(self, k, v)

        self.backend = self.get_backend()
        for resource in self.resources:
            resource.contribute_api(self.backend)

    def register_resource(self, resource):
        """Register a resource with the Api

        This will cause the resource's backend attribute to be
        populated.

        :param resource Resource:
        """
        self.resources.append(resource)

        # Pass the backend to the model if we have the backend available
        if self.backend:
            resource.contribute_api(self.backend)

    def get_backend_class(self):
        return self.backend_class

    def get_backend(self):
        backend_class = self.get_backend_class()
        return backend_class(self.get_base_url())

    def get_base_url(self):
        return self.base_url

    def __getattr__(self, item):
        """ Proxy the backend's attributes for convenience
        """
        if hasattr(self.backend, item):
            return getattr(self.backend, item)
        else:
            raise AttributeError(
                "Attribute {} could not be found on Api or ApiBackend".format(item)
            )


