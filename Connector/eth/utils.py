#!/usr/bin/python3
import json
import threading
import asyncio
import random
import sys
from .constants import *
from rpcutils import errorhandler as rpcErrorHandler, constants as rpcConstants
from wsutils.subscriptionshandler import SubcriptionsHandler
from . import apirpc
from logger import logger


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


def searchAddressesIntoBlock(data):

    if not SubcriptionsHandler.coinInAddressSubscription():
        logger.printWarning("Coin not available in subscriptions handler")
        return
    
    if not SubcriptionsHandler.getSubscriptionsAvailable():
        logger.printWarning("There are no addresses subscribed for")
        return

    reqParsed = None
    try:
        reqParsed = json.loads(data)
    except Exception as e:
        logger.printError(f"Payload is not JSON message. Error: {e}")
        raise rpcErrorHandler.BadRequestError(f"Payload is not JSON message. Error: {e}")
    
    params = reqParsed[rpcConstants.PARAMS]
    blockNumber = params[rpcConstants.RESULT][NUMBER]

    logger.printInfo(f"Getting new block to check addresses subscribed for. Block number: {params[rpcConstants.RESULT][NUMBER]}")
    block = apirpc.getBlockByNumber(
        random.randint(1, sys.maxsize),
        {
            BLOCK_NUMBER: blockNumber
        }
    )

    for address in SubcriptionsHandler.getSubscriptionsAvailable():
        for transaction in block[TRANSACTIONS]:
            if address == transaction[FROM] or address == transaction[TO]:
                notifyThread = threading.Thread(target=notifyHandler, args=(address,), daemon=True)
                notifyThread.start()


def notifyHandler(args):

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(notify(args))
    loop.close()


async def notify(address):

    addressClients = SubcriptionsHandler.getAddressClients(address)

    logger.printInfo(f"Getting balance for address subscribed for in new block. Address: {address}")
    balance = apirpc.getAddressBalance(
        random.randint(1, sys.maxsize),
        {
            ADDRESS: address
        }
    )

    logger.printInfo("Sending balance to subscribers")

    for client in addressClients:

        await client.websocket.send_str(
            json.dumps(
                balance
            )
        )


def getSyncPercentage(currentBlock, latestBlock):
    return (currentBlock * 100) / latestBlock