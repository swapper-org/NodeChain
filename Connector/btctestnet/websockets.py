from .constants import *
from .connector import BITCOIN_CALLBACK_PATH, ELECTRUM_NAME
from wsutils import wsutils
from wsutils.subscriptionshandler import SubcriptionsHandler
from rpcutils import rpcutils
from . import apirpc
from webapp import WebApp
from aiohttp import web
import random
import sys
import socket
import json
from logger import logger


@wsutils.webSocket
def bitcoinWS():
    app = WebApp()
    logger.printInfo("Starting WS for bitcoin callback")
    app.add_routes([web.post(BITCOIN_CALLBACK_PATH, bitcoinCallback)])


async def bitcoinCallback(request):

    if request.remote != socket.gethostbyname(ELECTRUM_NAME):
        return

    requestBody = await request.read()

    messageLoaded = json.loads(requestBody)

    if not SubcriptionsHandler.coinInAddressSubscription():
       logger.printWarning("There are no subscribers")
       return
    
    clients = SubcriptionsHandler.getAddressClients(messageLoaded[ADDRESS])

    if SubcriptionsHandler.addressHasClients(messageLoaded[ADDRESS]):

        id = random.randint(1, sys.maxsize)
        response = apirpc.getAddressBalance(
            id,
            {
                ADDRESS: messageLoaded[ADDRESS]
            }
        )

        for client in clients:
            await client.websocket.send_str(
                json.dumps(
                    rpcutils.generateRPCResultResponse(
                        id, 
                        response
                    )
                )
            )
