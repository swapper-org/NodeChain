#!/usr/bin/python3
import aiohttp
import asyncio
import json
import random
import sys
import threading
from logger.logger import Logger
from rpcutils import rpcutils, constants as rpcConstants, error
from wsutils.clientwebsocket import ClientWebSocket
from wsutils import topics, websocket
from wsutils.broker import Broker
from wsutils.publishers import Publisher
from . import apirpc, utils
from .constants import *


@websocket.WebSocket
class WebSocket:

    def __init__(self, coin, config):
        self._coin = coin
        self._config = config
        self._session = None
        self._loop = None

    async def start(self):

        Logger.printDebug("Starting WS for Ethereum")

        threading.Thread(
            target=self.ethereumWSThread,
            daemon=True
        ).start()

    def ethereumWSThread(self):

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        asyncio.ensure_future(self.ethereumClient(), loop=self.loop)
        self.loop.run_forever()

    async def ethereumClient(self):

        while True:
            async with ClientWebSocket(self.config.wsEndpoint) as session:
                self.session = session
                Logger.printDebug(f"Connecting to {self.config.wsEndpoint}")
                await session.connect()

                payload = {
                    rpcConstants.ID: random.randint(1, sys.maxsize),
                    rpcConstants.METHOD: SUBSCRIBE_METHOD,
                    rpcConstants.PARAMS: [
                        NEW_HEADS_SUBSCRIPTION
                    ]
                }

                Logger.printDebug(f"Subscribing to {NEW_HEADS_SUBSCRIPTION}")
                Logger.printDebug(f"Making request {payload} to {self.config.wsEndpoint}")

                await session.send(payload)

                closed = False
                async for msg in session.websocket:

                    if msg.type == aiohttp.WSMsgType.TEXT:

                        Logger.printInfo(f"Message received for {self.coin} websocket from {self.config.wsEndpoint}: {msg.data}")

                        if msg.data == 'close':
                            closed = True
                            await session.close()

                        else:
                            try:
                                payload = json.loads(msg.data)
                                if rpcConstants.PARAMS in payload:
                                    await self.ethereumWSWorker(payload[rpcConstants.PARAMS])
                                else:
                                    Logger.printError(f"No params in {self.coin} ws node message")
                            except Exception as e:
                                Logger.printError(f"Payload is not JSON message: {e}")

                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        break

                if not closed:
                    await session.close()

    async def ethereumWSWorker(self, params):

        blockNumber = params[rpcConstants.RESULT]["number"]

        Logger.printDebug(f"Getting new block to check addresses subscribed for. Block number: "
                          f"{params[rpcConstants.RESULT]['number']}")

        broker = Broker()
        publisher = Publisher()
        id = random.randint(1, sys.maxsize)

        try:
            block = await apirpc.getBlockByNumber(
                random.randint(1, sys.maxsize),
                {
                    "blockNumber": blockNumber
                },
                self.config
            )

            publisher.publish(
                broker=broker,
                topic=f"{self.coin}{topics.TOPIC_SEPARATOR}"
                      f"{self.config.networkName}{topics.TOPIC_SEPARATOR}"
                      f"{topics.NEW_BLOCKS_TOPIC}",
                message=rpcutils.generateRPCResultResponse(
                    id,
                    block
                )
            )

        except error.RpcBadRequestError as err:
            Logger.printError(f"Can not get new block. {err}")
            publisher.publish(broker, topics.NEW_BLOCKS_TOPIC, err.jsonEncode())
            return

        for address in broker.getSubTopics(f"{self.coin}{topics.TOPIC_SEPARATOR}"
                                           f"{self.config.networkName}{topics.TOPIC_SEPARATOR}"
                                           f"{topics.ADDRESS_BALANCE_TOPIC}"):

            if utils.isAddressInBlock(address, block["block"]):

                try:
                    balanceResponse = await apirpc.getAddressBalance(
                        id,
                        {
                            "address": address
                        },
                        self.config
                    )

                    publisher.publish(
                        broker=broker,
                        topic=f"{self.coin}{topics.TOPIC_SEPARATOR}{self.config.networkName}{topics.TOPIC_SEPARATOR}"
                              f"{topics.ADDRESS_BALANCE_TOPIC}{topics.TOPIC_SEPARATOR}{address}",
                        message=rpcutils.generateRPCResultResponse(
                            id,
                            balanceResponse
                        )
                    )
                except error.RpcBadRequestError as err:
                    Logger.printError(f"Can not get address balance for [{address}] {err}")
                    publisher.publish(broker, topics.NEW_BLOCKS_TOPIC, err.jsonEncode())
                    return

    async def stop(self):
        await self.session.close()
        self.loop.stop()

    @property
    def coin(self):
        return self._coin

    @property
    def config(self):
        return self._config

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        self._session = value

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value):
        self._loop = value
