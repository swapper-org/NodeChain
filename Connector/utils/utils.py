#!/usr/bin/python
import json
from httputils import error
from logger.logger import Logger
from .constants import *
from functools import lru_cache


def getAvailableCurrenciesFile():
    return getConfigProperty(AVAILABLE_CURRENCIES_FILE_PROPERTY)


def getConfigProperty(propertyName):

    try:
        with open(CONFIG_JSON, "r") as fp:
            config = json.load(fp)

            if propertyName not in config:
                Logger.printError(f"Configuration property {propertyName} could not be found")
                raise error.InternalServerError()
            return config[propertyName]

    except Exception as e:
        Logger.printError(f"Can not open configuration file: {str(e)}")
        raise error.InternalServerError()


def getAvailableCurrencies():

    availableCurrenciesFile = getAvailableCurrenciesFile()

    try:

        with open(availableCurrenciesFile) as file:
            config = json.load(file)
            return [conf["token"] for conf in config if "token" in conf]

    except Exception as e:
        Logger.printError(f"Can not open configuration file: {str(e)}")
        raise error.InternalServerError(f"Can not open configuration file: {str(e)}")


def isAvailableCurrency(coin):

    availableCurrenciesFile = getAvailableCurrenciesFile()

    try:

        with open(availableCurrenciesFile) as file:
            config = json.load(file)
            return coin in [conf["token"] for conf in config if "token" in conf]

    except FileNotFoundError as err:
        Logger.printError(f"File {availableCurrenciesFile} could not be found")
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
        Logger.printError(f"File {availableCurrenciesFile} could not be found")
        raise error.InternalServerError(f"File {availableCurrenciesFile} could not be found:{err}")


@lru_cache(maxsize=150)
def openSchemaFile(schemaFile):

    try:
        with open(schemaFile) as file:
            return json.load(file)
    except FileNotFoundError as err:
        Logger.printError(f"Schema {schemaFile} not found: {err}")
        raise error.InternalServerError("Unknown error")


def getMaxPage(numElements, pageSize=None):

    if not pageSize:
        pageSize = DEFAULT_PAGE_SIZE

    return numElements // pageSize if (numElements % pageSize) == 0 else (numElements // pageSize) + 1


def removeDuplicates(elements):

    seen = set()
    seen_add = seen.add
    return [x for x in elements if not (x in seen or seen_add(x))]


def paginate(elements, page=None, pageSize=None, side="left"):

    if side == "left":
        return lpaginate(elements=elements, page=page, pageSize=pageSize)
    if side == "right":
        return rpaginate(elements=elements, page=page, pageSize=pageSize)

    Logger.printError("Value for side parameter not valid in paginate function")
    raise error.InternalServerError("Internal server error")


def lpaginate(elements, page=None, pageSize=None):

    if not pageSize:
        pageSize = DEFAULT_PAGE_SIZE

    if not page:
        page = DEFAULT_PAGE

    return elements[pageSize * page:pageSize * (page + 1)]


def rpaginate(elements, page=None, pageSize=None):

    if not pageSize:
        pageSize = DEFAULT_PAGE_SIZE

    if not page:
        page = DEFAULT_PAGE

    return elements[len(elements) - (pageSize * (page + 1)):len(elements) - pageSize * page]

def saveTransactionLog(currencyName, txId):
    with open(TRANSACTIONS_LOG_FILE, mode="a") as file:
        file.write(currencyName + "," + txId)
