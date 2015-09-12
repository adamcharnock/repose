import requests

from repose import utilities


class ApiBackend(object):
    """Default backend implementation providing HTTP access to the remote API

    This can be extended and passed into your :class:`Api <repose.api.Api>`
    instance at instantiation time. This can be useful if you need to
    customise how requests are made, or how responses are parsed.
    """

    def __init__(self, base_url):
        """ Instantiate this class

        Args:

            base_url (str): The fully-qualified base URL to the the API.
                (Eg: ``"http://example.com"``).

        """
        self.base_url = base_url

    def make_url(self, endpoint):
        """ Construct the fully qualified URL for the given endpoint.

        For example::

            >>> my_backend = ApiBackend(base_url="http://example.com/api")
            >>> my_backend.make_url("/user/1")
            "http://example.com/api/user/1"

        Args:

            endpoint (str): The API endpoint (Eg: ``"/user/1"``).

        Returns:

            str: The fully qualified URL

        """
        return '{}/{}'.format(self.base_url.rstrip('/'), endpoint.lstrip('/'))

    def parse_response(self, response):
        """ Parse a response into a Python structure

        Args:

            response (:class:`requests.Response`): A Response object, unless otherwise
                provided by the :meth:`get`

        Returns:

            object: Typically a python list or dictionary
        """
        response.raise_for_status()
        return response.json()

    def get(self, endpoint, params=None):
        """ Perform a HTTP GET request for the specified endpoint

        Args:

            params (dict): Dictionary of URL params

        Returns:

            object: Typically a python list or dictionary
        """
        r = requests.get(self.make_url(endpoint), params=params)
        return self.parse_response(r)

    def put(self, endpoint, json):
        """ Perform a HTTP PUT request for the specified endpoint

        Args:

            json (dict): The JSON body to post with the request

        Returns:

            object: Typically a python list, dictionary, or None
        """
        r = requests.put(self.make_url(endpoint), json=json)
        return self.parse_response(r)

    def post(self, endpoint, json):
        """ Perform a HTTP POST request for the specified endpoint

        Args:

            json (dict): The JSON body to post with the request

        Returns:

            object: Typically a python list, dictionary, or None
        """
        r = requests.post(self.make_url(endpoint), json=json)
        return self.parse_response(r)

    def delete(self, endpoint, json):
        """ Perform a HTTP DELETE request for the specified endpoint

        Args:

            json (dict): The JSON body to post with the request

        Returns:

            object: Typically a python list, dictionary, or None
        """
        r = requests.delete(self.make_url(endpoint), json=json)
        return self.parse_response(r)
