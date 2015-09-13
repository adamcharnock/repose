Getting Started
===============

Repose allows you to declaratively define a client for restful
APIs. There are three steps to getting started:

1. :ref:`Define your resources <step1>`
2. :ref:`Configure your API <step2>`
3. :ref:`Try it out <step3>`

.. _step1:

1. Define your resources
------------------------

Each :class:`~repose.resources.Resource` you define will generally map
to a resource in your Api. Using GitHub's API as an example::

    class User(Resource):
        id = fields.Integer()
        login = fields.String()
        avatar_url = fields.String()
        location = fields.String()
        site_admin = fields.Boolean()

        class Meta:
            # Endpoint for getting a single specific user
            endpoint = '/users/{login}'
            # Endpoint for listing all users
            endpoint_list = '/users'

    class Repository(Resource):
        id = fields.Integer()
        name = fields.String()
        full_name = fields.String()
        description = fields.String()
        owner = fields.Embedded(User)

        class Meta:
            # Endpoint for getting a single specific repository
            endpoint = '/repos/{full_name}'
            # Endpoint for listing all repositories
            endpoint_list = '/repositories'

This represents a very small subset of the available GitHub API,
but it serves well as a demonstration.

.. seealso::

    See the :class:`~repose.resources.Resource` class for more in-depth details
    regarding resource definition. Also see the :mod:`repose.fields` module
    for a list of available fields.

.. _step2:

2. Configure your API
---------------------

To configure your API you need to :meth:`instantiate <repose.api.Api.__init__>` an
:class:`~repose.api.Api` class. You can customise the Api's
behaviour either through parameters to :meth:`~repose.api.Api.__init__()`
or by defining your own subclass of :class:`~repose.api.Api`.

In addition to providing high-level configuration, the Api instance
must also be made aware of all available resources.

For example::

    # A simple example of directly instantiating the Api class
    github_api = Api(base_url='https://api.github.com')
    github_api.register_resource(User)
    github_api.register_resource(Repository)

Or, using extension::

    # Alternatively, extend the Api class for added customisation options
    class GitHubApi(Api):
        base_url = 'https://api.github.com'
        resources = [User, Repository]

    github_api = GitHubApi()

The former is simpler, whereas the latter provides more flexibility for
overriding the base :class:`~repose.api.Api` class functionality.

.. seealso::

    See the :class:`~repose.api.Api` class for more in-depth details
    regarding Api definitions.

.. _step3:

3. Try it out
-------------

Now let's try it out and get some resources:

.. code-block:: python

    # Provide the login to get a user
    # (as this is what we specified in Meta.endpoint)
    >>> User.objects.get(login='adamcharnock')
    <__main__.User(login=u'adamcharnock', site_admin=None, id=138215, avatar_url=u'https://avatars.githubusercontent.com/u/138215?v=3', location=u'London, UK')>

    # Provide the full_name to get a repository
    # (again, as this is what we specified in Meta.endpoint)
    >>> seed_repo = Repository.objects.get(full_name='adamcharnock/seed')
    >>> seed_repo.description
    'A utility for easily creating and releasing Python packages'

    # The repo's owner attribute will give us a User resource
    # as this is an `Embedded` field
    >>> seed_repo.owner
    <__main__.User(login=u'adamcharnock', site_admin=None, id=138215, avatar_url=u'https://avatars.githubusercontent.com/u/138215?v=3', location=None)>

Ok, now let's get a list of all repositories:

.. code-block:: python

    >>> Repository.objects.count()
    100 # That cannot be right...
    >>> repos = Repository.objects.all()
    >>> len(repos)
    100

So we get some results, but only a hundred repositories in GitHub? That
definitly sounds wrong. What is going on here then?

.. todo::

    Implement pagination support

.. todo::

    Discuss limitations of ``count()``. Link into 'Using Managers' document
    where we'll discuss customising managers to provide this
    functionality.
