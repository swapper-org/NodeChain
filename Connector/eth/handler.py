#!/usr/bin/python
from httputils.router import CurrencyHandler
from httputils import httpmethod
from rpcutils import rpcutils, rpcmethod, error
from wsutils import wsmethod, websocket
from utils import utils
from logger import logger
from .websockets import WebSocket
from .connector import Config


@CurrencyHandler
class Handler:
    def __init__(self, coin):
        self._coin = coin
        self._networksConfig = {}

    def addConfig(self, network, config):

        if network in self.networksConfig:
            logger.printError(f"Configuration {network} already added for {self.coin}")
            return False, f"Configuration {network} already added for {self.coin}"

        defaultConfig, err = utils.loadDefaultPackageConf(self.coin)
        if err is not None:
            return False, err

        # TODO: Check error when host can not be found

        self.networksConfig[network] = Config(
            networkName=network,
            config={
                "protocol": config["protocol"] if "protocol" in config else defaultConfig["protocol"],
                "host": config["host"] if "host" in config else defaultConfig["host"],
                "rpcPort": config["rpcPort"] if "rpcPort" in config else defaultConfig["rpcPort"],
                "wsPort": config["wsPort"] if "wsPort" in config else defaultConfig["wsPort"]
            }
        )

        WebSocket(
            coin=self.coin,
            config=self.networksConfig[network]
        )

        websocket.startWebSockets(self.coin, self.networksConfig[network].networkName)

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
                                       networkName=self.networksConfig[network].networkName)

        del self.networksConfig[network]

        # TODO: Close all topics for this currency and this network

        return True, None

    async def updateConfig(self, network, config):

        if network not in self.networksConfig:
            logger.printError(f"Configuration {network} not added for {self.coin}")
            return False, f"Configuration {network} not added for {self.coin}"

        defaultConfig, err = utils.loadDefaultPackageConf(self.coin)
        if err is not None:
            return False, err

        await websocket.stopWebSockets(coin=self.coin,
                                       networkName=self.networksConfig[network].networkName
                                       )

        self.networksConfig[network] = Config(
            networkName=network,
            config={
                "protocol": config["protocol"] if "protocol" in config else defaultConfig["protocol"],
                "host": config["host"] if "host" in config else defaultConfig["host"],
                "rpcPort": config["rpcPort"] if "rpcPort" in config else defaultConfig["rpcPort"],
                "wsPort": config["wsPort"] if "wsPort" in config else defaultConfig["wsPort"]
            }
        )

        WebSocket(
            coin=self.coin,
            config=self.networksConfig[network]
        )

        websocket.startWebSockets(self.coin, self.networksConfig[network].networkName)

        return True, None

    async def handleRequest(self, network, method, request):

        if rpcutils.isRpcEnpointPath(method):
            return await rpcmethod.callMethod(
                coin=self.coin,
                request=request,
                config=self.networksConfig[network]
            )
        else:
            try:
                return await httpmethod.callMethod(
                    coin=self.coin,
                    method=method,
                    request=request,
                    config=self.networksConfig[network]
                )
            except error.RpcError as err:
                raise err.parseToHttpError()

    async def handleWsRequest(self, network, request):

        return await wsmethod.callMethod(
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


Handler("eth")
