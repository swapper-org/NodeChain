#!/usr/bin/python
from httputils.router import CurrencyHandler
from httputils import httpmethod
from rpcutils import rpcmethod, error
from wsutils import wsmethod, websocket, topics
from wsutils.broker import Broker
from logger import logger
from .websockets import AddressBalanceWs, BlockWebSocket
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

        # AddressBalanceWs(
        #     coin=self.coin,
        #     config=self.networksConfig[network]
        # )

        # BlockWebSocket(
        #     coin=self.coin,
        #     config=self.networksConfig[network]
        # )

        # await websocket.startWebSockets(
        #     coin=self.coin,
        #     networkName=network
        # )

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

        del self.networksConfig[network]

        # await websocket.stopWebSockets(
        #    coin=self.coin,
        #     networkName=network
        # )

        # broker = Broker()
        # pkgTopics = broker.getSubTopics(topicName=f"{self.coin}{topics.TOPIC_SEPARATOR}{network}")

        # for topic in list(pkgTopics):
        #     for subscriber in list(broker.getTopicSubscribers(topic)):
        #         subscriber.close(broker=broker)

        return True, None

    async def updateConfig(self, network, config):

        if network not in self.networksConfig:
            logger.printError(f"Configuration {network} not added for {self.coin}")
            return False, f"Configuration {network} not added for {self.coin}"

        ok, err = self.networksConfig[network].loadConfig(config=config)
        if not ok:
            logger.printError(f"Can not load config for {network} for {self.coin}: {err}")
            return ok, err

        # await websocket.stopWebSockets(
        #     coin=self.coin,
        #     networkName=network
        # )

        # AddressBalanceWs(
        #     coin=self.coin,
        #     config=self.networksConfig[network]
        # )

        # BlockWebSocket(
        #     coin=self.coin,
        #     config=self.networksConfig[network]
        # )

        # websocket.startWebSockets(
        #     coin=self.coin,
        #     networkName=network
        # )

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

    async def handleCallback(self, network, callbackName, request):

        return await httpmethod.callCallbackMethod(
            coin=self.coin,
            callbackName=callbackName,
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
