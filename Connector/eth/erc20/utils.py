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


def addressIsInvolvedInTx(address, contract, transaction):

    # Transaction is made to the desire erc-20 contract
    if transaction["to"] is None or transaction["to"] != contract.address:
        return False

    # Transaction is made from the desire address
    if transaction["from"]["address"] == address:
        return True

    # Transaction is made to the desire address
    try:
        func_obj, func_params = contract.decode_function_input(transaction["inputData"])
        return func_params["_to"] == address
    except ValueError:
        return False
