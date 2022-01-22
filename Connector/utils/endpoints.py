#/usr/bin/python
import json
from rpcutils import errorhandler as rpcerrorhandler
from logger import logger
from .constants import *


def getVersion(id, params):

    logger.printInfo("Executing RPC method getVersion")

    try:
        with open(CONFIG_JSON, "r") as fp:
            config = json.load(fp)

    except Exception as e:
        logger.printError(str(e))
        raise rpcerrorhandler.InternalServerError(str(e))

    return {
        VERSION: config[VERSION] if VERSION in config else "Unknown"
    }
