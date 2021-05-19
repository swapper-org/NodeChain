import threading
import random
import asyncio
import sys
import aiohttp
from wsutils.clientwebsocket import ClientWebSocket
from wsutils import wsutils
from rpcutils import constants as rpcConstants
from .constants import *
from .connector import WS_ENDPOINT
from . import utils
from logger import logger


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
                    addrSearcherThread = threading.Thread(target=utils.searchAddressesIntoBlock, args=(msg.data,), daemon=True)
                    addrSearcherThread.start()

            elif msg.type == aiohttp.WSMsgType.ERROR:
                break
