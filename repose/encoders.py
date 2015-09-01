from booby.encoders import *
from booby.helpers import nullable


class ModelToIdListEncoder(Encoder):

    @nullable
    def encode(self, value):
        return [m.id for m in value]
