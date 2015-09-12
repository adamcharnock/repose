"""
Managers have the task of managing access to resources.

.. note:: Managers are modelled after
    `Django's ORM Managers <https://docs.djangoproject.com/en/dev/topics/db/managers/>`_.

For example, to access a group of fictional ``User``
resources you would use::

    # Simple user of a manager
    users = User.objects.all()

Here you access the ``objects`` manager on the ``User`` resource. The
``objects`` manager is known as the 'default' manager. Additional
managers may also by provided. For example::

    class User(Resource):
        ... define fields...

        # Note you need to explicitly define the 'objects' default
        # manager when you add custom managers
        objects = Manager()

        # Now add some custom managers
        active_users = Manager(filter=lambda u: u.is_active)
        inactive_users = Manager(filter=lambda u: not u.is_active)
        super_users = Manager(filter=lambda u: u.is_super_user)

Now you can use statements such as::

    awesome_users = User.super_users.all()
    total_active_users = User.active_users.count()

You can also extend the :class:`Manager` class to provide both additional
functionality and greater intelligence. For example::

    class UserManager(Manager):

        def count(self):
            # Pull the count from the server rather than pulling all
            # users then counting them.
            json = self.api.get('/users/total_count')
            return json['total']

Or perhaps you want be able to perform custom actions on groups of
Resources::

    class LightManager(manager):

        def turn_on(self):
            for light in self.all():
                light.on = True
                light.save()

"""

from repose.utilities import get_values_from_endpoint


class Manager(object):
    """ The base Manager class

    Attributes:

        api (Api): The Api instance
        decoders (list[Decoder]): The decoders used to decode list data
        model (:class:`~repose.resources.Resource`): The Resource class to be managed
        results (list): The results as loaded from the API
        results_endpoint (list): The results to be used to fetch results

    """
    model = None
    results = None
    results_endpoint = None

    def __init__(self, decoders=None, results_endpoint=None, filter=None):
        """ Initialise the Manager

        Args:

            decoders (list[Decoder]): The decoders used to decode list data
            results_endpoint (str): The results to be used to fetch results. Defaults to
                :attr:`Meta.endpoint_list`
            filter (callable): The filter function to be applied to the results.
                Will be passed a single result and must return True/False
                if the result should be included/excluded in the results
                respectively.
        """
        self.decoders = decoders or []
        self.results_endpoint = results_endpoint
        self.filter_fn = filter

    def get(self, **endpoint_params):
        """Get a single resource

        Args:

            endpoint_params (dict): Parameters which should be used to format the
                 :attr:`Meta.endpoint` string.

        Returns:

            Resource:
        """
        endpoint = self.model.Meta.endpoint.format(**endpoint_params)
        data = self.api.get(endpoint)
        decoded = self.model.decode(data)
        decoded.update(**get_values_from_endpoint(self.model, endpoint_params))
        return self.model(**decoded)

    def _load_results(self):
        """Load all the results for this manager

        Returns:

            None
        """
        if self.results is not None:
            return
        data = self.api.get(self.get_results_endpoint())
        for decoder in self.get_decoders():
            data = decoder(data)
        self.results = [self.model(**self.model.decode(d)) for d in data]

    def get_decoders(self):
        """ Return the decoders to be used for decoding list data

        Returns:

            list[Decoder]: :attr:`Manager.decoders` by default
        """
        return self.decoders

    def get_results_endpoint(self):
        """ Get the results endpoint

        Returns:

            str: ``results_endpoint`` as passed to :func:`__init__` or :attr:`Meta.endpoint_list`.
        """
        return self.results_endpoint or self.model.Meta.endpoint_list

    def contribute_to_class(self, model):
        self.model = model

    @classmethod
    def contribute_api(cls, api):
        cls._api = api

    @property
    def api(self):
        try:
            return self._api
        except AttributeError:
            raise AttributeError(
                "Api not available on {}. Either you haven't instantiated "
                "an Api instance, or you haven't registered your resource "
                "with your Api instance.".format(self))

    def filter(self, results):
        if self.filter_fn:
            return list(filter(self.filter_fn, results))
        else:
            return results

    def all(self):
        """ Return all results
        """
        self._load_results()
        return self.filter(self.results)

    def __iter__(self):
        return iter(self.all())

    def count(self):
        """ Return the total number of results

        Returns:

            int

        .. note::

            This is a naive implementation of ``count()`` which simply
            retrieves all results and counts them. You should
            consider overriding this (as demoed above) if dealing
            with non-trivial numbers of results.

        """
        return len(self.all())
