import json
import os
from .rpcutils import rpcMethod
from .errorhandler import InternalServerError
from .constants import *
from logger import logger
from httputils import httputils


@httputils.getMethod
@rpcMethod
def getVersion(id, params):

    logger.printInfo("Executing RPC method getVersion")

    try:
        file = os.path.join(".", CONFIG_JSON)
        with open(file, "r") as fp:
            config = json.load(fp)

    except Exception as e:
        logger.printError(str(e))
        raise InternalServerError(str(e))

    return {
        VERSION: config[VERSION] if VERSION in config else UNKNOWN
    }
