#!/usr/bin/python3
from aiohttp import web
import json
import random
import socket
import sys
from logger import logger
from rpcutils import rpcutils
from wsutils import wsutils, topics
from wsutils.broker import Broker
from wsutils.publishers import Publisher
from webapp import WebApp
from .constants import *
from .connector import BITCOIN_CALLBACK_PATH, ELECTRUM_NAME
from . import apirpc


@wsutils.webSocket
def bitcoinWS():
    app = WebApp()
    logger.printInfo("Starting WS for bitcoin callback")
    app.add_routes([web.post(BITCOIN_CALLBACK_PATH, bitcoinCallback)])


async def bitcoinCallback(request):

    if request.remote != socket.gethostbyname(ELECTRUM_NAME):
        return

    requestBody = await request.read()

    broker = Broker()
    messageLoaded = json.loads(requestBody)

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
