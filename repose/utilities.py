from _socket import gethostname
from collections import MutableSequence
import json
import os
import requests
from repose import exceptions


USERNAME_SAVE_PATH = '~/.python_hue'


def parse_response(response):
    json = response.json()

    if json is list and len(json) > 0 and 'error' in json:
        error = json['error']
        exception = {
            '101': exceptions.LinkButtonNotPressed,
        }.get(str(error.get('type')), exceptions.HueApiException)
        raise exception(error.get('description'))

    return json


def authenticate(app_name, bridge_host='philips-hue', client_name=None):
    client_name = client_name or gethostname()

    url = 'http://{bridge_host}/api'.format(**locals())
    r = requests.post(url, json={
        'devicetype': '{}#{}'.format(app_name, client_name),
    })
    return parse_response(r)['username']


def authenticate_interactive(app_name=None, bridge_host=None, client_name=None):
    host_name = gethostname()

    bridge_host = raw_input("Philips Hue Bridge IP address or "
                            "host name [philips-hue]: "
                            ).strip() or 'philips-hue'
    app_name = raw_input("Your application name [test-app]").strip() or 'test-app'
    client_name = raw_input("Your device name [{}]" .format(host_name)).strip() or host_name

    username = None
    while not username:
        raw_input('Now press the link button on the Hue Bridge. Press enter when done.')
        try:
            username = authenticate(
                bridge_host=bridge_host, app_name=app_name, client_name=client_name)
        except exceptions.LinkButtonNotPressed:
            print 'Error, link button not pressed, trying again...'

    print 'Your username is: {}'.format(username)

    if raw_input('Save username to {} [Y/n]?'.format(USERNAME_SAVE_PATH)) != 'n':
        save_username(username)


def save_username(username):
    with open(os.path.expanduser(USERNAME_SAVE_PATH), 'w') as f:
        f.write(json.dumps({
            'philips-hue': {
                'username': username,
            }
        }))


def load_username():
    try:
        with open(os.path.expanduser(USERNAME_SAVE_PATH), 'r') as f:
            contents = f.read()
    except IOError:
        return None
    return json.loads(contents)['philips-hue']['username']


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
