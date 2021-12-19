#!/usr/bin/python3
from aiohttp import web
import asyncio
import binascii
import json
import random
import socket
import sys
import threading
import zmq
import zmq.asyncio
from logger import logger
from rpcutils import rpcutils, errorhandler as rpcerrorhandler
from wsutils import wsutils, topics
from wsutils.broker import Broker
from wsutils.publishers import Publisher
from webapp import WebApp
from .constants import *
from .connector import BITCOIN_CALLBACK_PATH, ELECTRUM_NAME, ZMQ_CORE_ENDPOINT
from . import apirpc


@wsutils.webSocket
def addressBalanceWS():
    app = WebApp()
    logger.printInfo("Starting WS for address balance callback")
    app.add_routes([web.post(BITCOIN_CALLBACK_PATH, addressBalanceCallback)])


@wsutils.webSocket
def newBlockWS():
    logger.printInfo("Starting WS for new blocks")
    thread = threading.Thread(target=newBlocksWSThread, daemon=True)
    thread.start()


async def addressBalanceCallback(request):

    if request.remote != socket.gethostbyname(ELECTRUM_NAME):
        return

    try:
        messageLoaded = json.loads(await request.read())
    except Exception as e:
        raise rpcerrorhandler.InternalServerError(f"Payload from {ELECTRUM_NAME} is not JSON message: {e}")

    broker = Broker()
    addrBalanceTopic = topics.ADDRESS_BALANCE_TOPIC + topics.TOPIC_SEPARATOR + messageLoaded[ADDRESS]

    if not broker.isTopic(addrBalanceTopic):
        logger.printWarning("There are no subscribers")
        return

    id = random.randint(1, sys.maxsize)
    response = apirpc.getAddressBalance(
        id,
        {
            ADDRESS: messageLoaded[ADDRESS]
        }
    )

    addrBalancePub = Publisher()
    addrBalancePub.publish(
        broker,
        addrBalanceTopic,
        rpcutils.generateRPCResultResponse(
            id,
            response
        )
    )


def newBlocksWSThread():

    logger.printInfo("Configuring ZMQ Socket")

    zmqContext = zmq.asyncio.Context()
    zmqSocket = zmqContext.socket(zmq.SUB)
    zmqSocket.setsockopt(zmq.RCVHWM, 0)
    zmqSocket.setsockopt_string(zmq.SUBSCRIBE, NEW_HASH_BLOCK_ZMQ_TOPIC)
    zmqSocket.connect(ZMQ_CORE_ENDPOINT)

    app = WebApp()
    app.addZMQSocket(zmqSocket)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(newBlocksWorker(zmqSocket))
    loop.close()


async def newBlocksWorker(zmqSocket):

    newBlockPub = Publisher()
    broker = Broker()

    while True:

        payload = await zmqSocket.recv_multipart()
        topic = payload[0].decode("utf-8")
        message = payload[1]

        if topic == NEW_HASH_BLOCK_ZMQ_TOPIC:

            blockHash = binascii.hexlify(message).decode("utf-8")
            logger.printInfo(f"New message for [{topic}]: {blockHash}")

            try:

                block = apirpc.getBlockByHash(
                    random.randint(1, sys.maxsize),
                    {
                        BLOCK_HASH: blockHash
                    }
                )

                newBlockPub.publish(broker, topics.NEW_BLOCKS_TOPIC, block)

            except rpcerrorhandler.BadRequestError as err:
                logger.printError(f"Error getting block {blockHash}: {err}")
                newBlockPub.publish(broker, topics.NEW_BLOCKS_TOPIC, err.jsonEncode())


@wsutils.webSocketClosingHandler
async def wsClosingHandler():

    logger.printInfo("Closing ZMQ connections")

    app = WebApp()
    await app.closeAllZMQSocket()

    logger.printInfo("Closing subscribers connections")

    broker = Broker()

    for topicName in broker.getTopicNameSubscriptions():
        for subscriber in list(broker.getTopicSubscribers(topicName)):
            await subscriber.closeConnection(broker)
