#!/usr/bin/python3
from logger import logger
from .constants import *


def ensureHash(hashAddr):
    if isinstance(hashAddr, str):
        if hashAddr.startswith('0x'):
            return hashAddr.lower()
        else:
            return '0x' + hashAddr.lower()
    else:
        return hashAddr.lower()


def getMethodSchemas(name):
    return getRequestMethodSchema(name), getResponseMethodSchema(name)


def getRequestMethodSchema(name):
    return RPC_JSON_SCHEMA_FOLDER + name + SCHEMA_CHAR_SEPARATOR + REQUEST + SCHEMA_EXTENSION


def getResponseMethodSchema(name):
    return RPC_JSON_SCHEMA_FOLDER + name + SCHEMA_CHAR_SEPARATOR + RESPONSE + SCHEMA_EXTENSION


def getWSMethodSchemas(name):
    return getWSRequestMethodSchema(name), getWSResponseMethodSchema(name)


def getWSRequestMethodSchema(name):
    return WS_JSON_SCHEMA_FOLDER + name + SCHEMA_CHAR_SEPARATOR + REQUEST + SCHEMA_EXTENSION


def getWSResponseMethodSchema(name):
    return WS_JSON_SCHEMA_FOLDER + name + SCHEMA_CHAR_SEPARATOR + RESPONSE + SCHEMA_EXTENSION


def isAddressInBlock(address, block):
    for transaction in block["transactions"]:
        if address.lower() == transaction["from"].lower() or address.lower() == transaction["to"].lower():
            return True
    return False


def getSyncPercentage(currentBlock, latestBlock):
    return (currentBlock * 100) / latestBlock


def closingAddrBalanceTopic(topicName):
    logger.printInfo(f"No need to handle topic [{topicName}] close")


def toWei(amount):
    return int(amount, 16)


def toHex(amount):
    return hex(amount)
