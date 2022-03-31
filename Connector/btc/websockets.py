#!/usr/bin/python3
# from aiohttp import web
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
from rpcutils import rpcutils, error
from wsutils import wsutils, topics
from wsutils.broker import Broker
from wsutils.publishers import Publisher
from .constants import *
from . import apirpc
from wsutils import websocket
from httputils import httpmethod


@websocket.WebSocket
class AddressBalanceWs:

    def __init__(self, coin, config):
        self._coin = coin
        self._config = config

    def start(self):

        # TODO: Check this is working properly
        broker = Broker()
        for address in broker.getSubTopics(topicName=f"{self.coin}{topics.TOPIC_SEPARATOR}"
                                                     f"{self.config.networkName}{topics.TOPIC_SEPARATOR}"
                                                     f"{topics.ADDRESS_BALANCE_TOPIC}"
                                           ):
            apirpc.notify(
                id=random.randint(1, sys.maxsize),
                params={
                    "address": address,
                    "callBackEndpoint": f"{self.config.bitcoinAddressCallbackHost}"
                                        f"/{self.coin}/{self.config.networkName}"
                                        f"/callback/{ADDR_BALANCE_CALLBACK_NAME}"
                },
                config=self.config
            )

    async def stop(self):

        # TODO: Check this is working properly
        broker = Broker()
        for address in broker.getSubTopics(topicName=f"{self.coin}{topics.TOPIC_SEPARATOR}"
                                                     f"{self.config.networkName}{topics.TOPIC_SEPARATOR}"
                                                     f"{topics.ADDRESS_BALANCE_TOPIC}"
                                           ):
            apirpc.notify(
                id=random.randint(1, sys.maxsize),
                params={
                    "address": address,
                    "callBackEndpoint": ""
                },
                config=self.config
            )

    @property
    def coin(self):
        return self._coin

    @property
    def config(self):
        return self._config


@httpmethod.callbackMethod(callbackName=ADDR_BALANCE_CALLBACK_NAME, coin=COIN_SYMBOL)
def addressBalanceCallback(request, config, coin):

    # TODO: Check the call is made from config [electrumHost]

    broker = Broker()
    addrBalanceTopic = f"{coin}{topics.TOPIC_SEPARATOR}" \
                       f"{config.networkName}{topics.TOPIC_SEPARATOR}" \
                       f"{topics.ADDRESS_BALANCE_TOPIC}{topics.TOPIC_SEPARATOR}" \
                       f"{request['address']}"

    if not broker.isTopic(addrBalanceTopic):
        logger.printWarning("There are no subscribers")
        return

    id = random.randint(1, sys.maxsize)
    response = apirpc.getAddressBalance(
        id=id,
        params={
            "address": request["address"]
        },
        config=config
    )

    Publisher().publish(
        broker,
        addrBalanceTopic,
        rpcutils.generateRPCResultResponse(
            id,
            response
        )
    )


@websocket.WebSocket
class BlockWebSocket:

    def __init__(self, coin, config):
        self._coin = coin
        self._config = config
        self._loop = None

    def start(self):

        logger.printInfo("Starting Block WS for Bitcoin")
        threading.Thread(
            target=self.newBlocksThread,
            daemon=True
        ).start()

    def newBlocksThread(self):

        logger.printInfo("Configuring ZMQ Socket")

        zmqContext = zmq.asyncio.Context()
        zmqSocket = zmqContext.socket(zmq.SUB)
        zmqSocket.setsockopt(zmq.RCVHWM, 0)
        zmqSocket.setsockopt_string(zmq.SUBSCRIBE, NEW_HASH_BLOCK_ZMQ_TOPIC)
        zmqSocket.connect(self.config.bitcoincoreZmqEndpoint)

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        asyncio.ensure_future(self.newBlocksWorker(zmqSocket), loop=self.loop)
        self.loop.run_forever()

    async def newBlocksWorker(self, zmqSocket):

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
                        id=random.randint(1, sys.maxsize),
                        params={
                            "blockHash": blockHash
                        },
                        config=self.config
                    )

                    newBlockPub.publish(
                        broker=broker,
                        topic=f"{self.coin}{topics.TOPIC_SEPARATOR}"
                              f"{self.config.networkName}{topics.TOPIC_SEPARATOR}"
                              f"{topics.NEW_BLOCKS_TOPIC}",
                        message=block
                    )

                except error.RpcBadRequestError as err:
                    logger.printError(f"Error getting block {blockHash}: {err}")
                    newBlockPub.publish(
                        broker=broker,
                        topic=f"{self.coin}{topics.TOPIC_SEPARATOR}"
                              f"{self.config.networkName}{topics.TOPIC_SEPARATOR}"
                              f"{topics.NEW_BLOCKS_TOPIC}",
                        message=err.jsonEncode()
                    )

    async def stop(self):
        self.loop.stop()

    @property
    def coin(self):
        return self._coin

    @property
    def config(self):
        return self._config

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value):
        self._loop = value
