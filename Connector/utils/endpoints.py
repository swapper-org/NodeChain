import json
import os
from httputils import httputils
from rpcutils import rpcutils
from rpcutils.errorhandler import InternalServerError
from rpcutils.constants import *
from logger import logger


@httputils.getMethod
@rpcutils.rpcMethod
def getVersion(id, params):

    logger.printInfo("Executing RPC method getVersion")

    try:
        with open(CONFIG_JSON, "r") as fp:
            config = json.load(fp)

    except Exception as e:
        logger.printError(str(e))
        raise InternalServerError(str(e))

    return {
        VERSION: config[VERSION] if VERSION in config else UNKNOWN
    }
