import json
import os
from .rpcutils import rpcMethod
from .errorhandler import InternalServerError
from .constants import *

@rpcMethod
def getVersion(id, params):

    try:
        file = os.path.join(".", CONFIG_JSON)
        with open(file, "r") as fp:
            config = json.load(fp)

    except Exception as e:
        raise InternalServerError(str(e))

    return {
        VERSION: config[VERSION] if VERSION in config else "Unknown"
    }