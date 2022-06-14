#!/usr/bin/python
from httputils.router import CurrencyHandler
from httputils import httpmethod
from rpcutils import rpcmethod, error
from wsutils import wsmethod, websocket, topics
from wsutils.broker import Broker
from logger import logger
from .websockets import WebSocket
from .config import Config
from .constants import COIN_SYMBOL


@CurrencyHandler
class Handler:

    def __init__(self, coin):
        self._coin = coin
        self._networksConfig = {}

    async def addConfig(self, network, config):

        if network in self.networksConfig:
            logger.printError(f"Configuration {network} already added for {self.coin}")
            return False, f"Configuration {network} already added for {self.coin}"

        pkgConfig = Config(
            coin=self.coin,
            networkName=network
        )

        ok, err = pkgConfig.loadConfig(config=config)
        if not ok:
            logger.printError(f"Can not load config for {network} for {self.coin}: {err}")
            return ok, err

        self.networksConfig[network] = pkgConfig

        WebSocket(
            coin=self.coin,
            config=self.networksConfig[network]
        )

        await websocket.startWebSockets(self.coin, network)

        return True, None

    def getConfig(self, network):

        if network not in self.networksConfig:
            logger.printError(f"Configuration {network} not added for {self.coin}")
            return None, f"Configuration {network} not added for {self.coin}"

        return self.networksConfig[network].jsonEncode(), None

    async def removeConfig(self, network):

        if network not in self.networksConfig:
            logger.printError(f"Configuration {network} not added for {self.coin}")
            return False, f"Configuration {network} not added for {self.coin}"

        await websocket.stopWebSockets(coin=self.coin,
                                       networkName=network)

        broker = Broker()
        pkgTopics = broker.getSubTopics(topicName=f"{self.coin}{topics.TOPIC_SEPARATOR}{network}")

        for topic in list(pkgTopics):
            for subscriber in list(broker.getTopicSubscribers(topic)):
                subscriber.close(broker=broker)

        del self.networksConfig[network]

        return True, None

    async def updateConfig(self, network, config):

        if network not in self.networksConfig:
            logger.printError(f"Configuration {network} not added for {self.coin}")
            return False, f"Configuration {network} not added for {self.coin}"

        await websocket.stopWebSockets(coin=self.coin,
                                       networkName=network
                                       )

        ok, err = self.networksConfig[network].loadConfig(config=config)
        if not ok:
            logger.printError(f"Can not load config for {network} for {self.coin}: {err}")
            return ok, err

        WebSocket(
            coin=self.coin,
            config=self.networksConfig[network]
        )

        websocket.startWebSockets(
            coin=self.coin,
            networkName=network
        )

        return True, None

    async def handleRPCRequest(self, network, standard, request):

        return await rpcmethod.RouteTableDef.callMethod(
            coin=self.coin,
            standard=standard,
            request=request,
            config=self.networksConfig[network]
        )

    async def handleHTTPRequest(self, network, standard, method, request):
        try:
            return await httpmethod.RouteTableDef.callMethod(
                coin=self.coin,
                standard=standard,
                method=method,
                request=request,
                config=self.networksConfig[network]
            )
        except error.RpcError as err:
            raise err.parseToHttpError()

    async def handleWsRequest(self, network, request):

        return await wsmethod.RouteTableDef.callMethod(
            coin=self.coin,
            request=request,
            config=self.networksConfig[network]
        )

    @property
    def coin(self):
        return self._coin

    @coin.setter
    def coin(self, value):
        self._coin = value

    @property
    def networksConfig(self):
        return self._networksConfig

    @networksConfig.setter
    def networksConfig(self, value):
        self._networksConfig = value


Handler(COIN_SYMBOL)
