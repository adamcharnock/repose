from repose.utilities import get_values_from_endpoint


class Manager(object):
    model = None
    results = None
    results_endpoint = None

    def __init__(self, decoders=None, results_endpoint=None, filter=None):
        self.decoders = decoders or []
        self.results_endpoint = results_endpoint
        self.filter_fn = filter

    def get(self, **endpoint_params):
        """Get a single model

        :param endpoint_params: dict Parameters which should be used to format the
                                     ``Meta.endpoint`` string
        """
        endpoint = self.model.Meta.endpoint.format(**endpoint_params)
        data = self.api.get(endpoint)
        decoded = self.model.decode(data)
        decoded.update(**get_values_from_endpoint(self.model, endpoint_params))
        return self.model(**decoded)

    def _load_results(self):
        """Load all the results for this manager"""
        if self.results is not None:
            return
        data = self.api.get(self.get_results_endpoint())
        for decoder in self.get_decoders():
            data = decoder(data)
        self.results = [self.model(**self.model.decode(d)) for d in data]

    def get_decoders(self):
        return self.decoders

    def get_results_endpoint(self):
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
        self._load_results()
        return self.filter(self.results)

    def __iter__(self):
        return iter(self.all())

    def count(self):
        return len(self.all())
