#!/usr/bin/python
import json
from .constants import *
from logger import logger
from httputils import error
from functools import lru_cache


def getMethodSchemas(name):
    return getRequestMethodSchema(name), getResponseMethodSchema(name)


def getRequestMethodSchema(name):
    return RPC_JSON_SCHEMA_FOLDER + name + SCHEMA_CHAR_SEPARATOR + REQUEST + SCHEMA_EXTENSION


def getResponseMethodSchema(name):
    return RPC_JSON_SCHEMA_FOLDER + name + SCHEMA_CHAR_SEPARATOR + RESPONSE + SCHEMA_EXTENSION


def getABISchema(name):
    return f"{ABI_FOLDER}{name}{SCHEMA_EXTENSION}"


@lru_cache(maxsize=9)
def getFunctionABI(fileName):

    try:
        with open(fileName) as file:
            return json.load(file)
    except FileNotFoundError as err:
        logger.printError(f"Schema {fileName} not found: {err}")
        raise error.InternalServerError(f"Schema {fileName} not found: {err}")
