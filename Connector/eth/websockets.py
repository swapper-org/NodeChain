#!/usr/bin/python3
import aiohttp
import asyncio
import json
import random
import sys
import threading
from logger import logger
from rpcutils import rpcutils, constants as rpcConstants, errorhandler as rpcErrorHandler
from wsutils.clientwebsocket import ClientWebSocket
from wsutils import wsutils, topics
from wsutils.broker import Broker
from wsutils.publishers import Publisher
from . import apirpc, utils
from .constants import *
from .connector import WS_ENDPOINT


@wsutils.webSocket
def ethereumWS():

    logger.printInfo("Starting WS for Ethereum")
    ethereumWSClient = threading.Thread(target=ethereumWSThread, args=("Eth daemon",), daemon=True)
    ethereumWSClient.start()


def ethereumWSThread(args):

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(ethereumClientCallback(args))
    loop.close()


async def ethereumClientCallback(request):

    async with ClientWebSocket(WS_ENDPOINT) as session:

        logger.printInfo(f"Connecting to {WS_ENDPOINT}")
        await session.connect()

        payload = {
            rpcConstants.ID: random.randint(1, sys.maxsize),
            rpcConstants.METHOD: SUBSCRIBE_METHOD,
            rpcConstants.PARAMS: [
                NEW_HEADS_SUBSCRIPTION,
                {
                    INCLUDE_TRANSACTIONS: True
                }
            ]
        }

        logger.printInfo(f"Subscribing to {NEW_HEADS_SUBSCRIPTION}")
        logger.printInfo(f"Making request {payload} to {WS_ENDPOINT}")

        await session.send(payload)

        async for msg in session.websocket:

            if msg.type == aiohttp.WSMsgType.TEXT:

                if msg.data == 'close':
                    await session.close()

                elif rpcConstants.PARAMS in msg.data:
                    addrSearcherThread = threading.Thread(target=ethereumWSWorker, args=(msg.data,), daemon=True)
                    addrSearcherThread.start()

            elif msg.type == aiohttp.WSMsgType.ERROR:
                break


def ethereumWSWorker(data):

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

    broker = Broker()
    addrBalancePub = Publisher()

    for address in broker.getSubTopics(topics.ADDRESS_BALANCE_TOPIC):
        if utils.isAdressInBlock(address, block):

            id = random.randint(1, sys.maxsize)
            balanceResponse = apirpc.getAddressBalance(
                id,
                {
                    ADDRESS: address
                }
            )

            addrBalancePub.publish(
                broker,
                topics.ADDRESS_BALANCE_TOPIC + topics.TOPIC_SEPARATOR + address,
                rpcutils.generateRPCResultResponse(
                    id,
                    balanceResponse
                )
            )


@wsutils.webSocketClosingHandler
async def wsClosingHandler():

    broker = Broker()

    for topicName in broker.getTopicNameSubscriptions():
        for subscriber in list(broker.getTopicSubscribers(topicName)):
            await subscriber.closeConnection(broker)
