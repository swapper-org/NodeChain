#!/usr/bin/python
import json
import os
from httputils import error, httputils
from logger import logger
from .constants import *


def getAvailableCurrenciesFile():
    return getConfigProperty(AVAILABLE_CURRENCIES_FILE_PROPERTY)


def getConfigProperty(propertyName):

    try:
        with open(CONFIG_JSON, "r") as fp:
            config = json.load(fp)

            if propertyName not in config:
                logger.printError(f"Configuration property {propertyName} could not be found")
                raise error.InternalServerError(f"Configuration property {propertyName} could not be found")
            return config[propertyName]

    except Exception as e:
        logger.printError(f"Can not open configuration file: {str(e)}")
        raise error.InternalServerError(f"Can not open configuration file: {str(e)}")


def getAvailableCurrencies():

    availableCurrenciesFile = getAvailableCurrenciesFile()

    try:

        with open(availableCurrenciesFile) as file:
            config = json.load(file)
            return [conf["token"] for conf in config if "token" in conf]

    except Exception as e:
        logger.printError(f"Can not open configuration file: {str(e)}")
        raise error.InternalServerError(f"Can not open configuration file: {str(e)}")


def isAvailableCurrency(coin):

    availableCurrenciesFile = getAvailableCurrenciesFile()

    try:

        with open(availableCurrenciesFile) as file:
            config = json.load(file)
            return coin in [conf["token"] for conf in config if "token" in conf]

    except FileNotFoundError as err:
        logger.printError(f"File {availableCurrenciesFile} could not be found")
        raise error.InternalServerError(f"File {availableCurrenciesFile} could not be found:{err}")


def isAvailableNetworkForCurrency(coin, network):

    availableCurrenciesFile = getAvailableCurrenciesFile()

    try:

        with open(availableCurrenciesFile) as file:
            config = json.load(file)

            for conf in config:
                if "token" in conf and conf["token"] == coin:
                    if "networks" in conf:
                        return network in conf["networks"]

        return False

    except FileNotFoundError as err:
        logger.printError(f"File {availableCurrenciesFile} could not be found")
        raise error.InternalServerError(f"File {availableCurrenciesFile} could not be found:{err}")
