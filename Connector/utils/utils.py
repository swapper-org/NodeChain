#!/usr/bin/python
import json
from httputils import error
from logger import logger
from .constants import *


def getAvailableCurrenciesFile():
    return getConfigProperty(AVAILABLE_CURRENCIES_FILE_PROPERTY)


def getConfigProperty(propertyName):

    try:
        with open(CONFIG_JSON, "r") as fp:
            config = json.load(fp)

            if "availableCurrenciesFile" not in config:
                logger.printError(f"Configuration property {propertyName} could not be found")
                raise error.InternalServerError(f"Configuration property {propertyName} could not be found")
            return config[propertyName]

    except Exception as e:
        logger.printError(f"Can not open configuration file: {str(e)}")
        raise error.InternalServerError(f"Can not open configuration file: {str(e)}")
