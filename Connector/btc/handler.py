#!/usr/bin/python
from httputils.router import CurrencyHandler
from httputils import httpmethod
from rpcutils import rpcutils, rpcmethod, error
from wsutils import wsmethod, websocket
from logger import logger
from utils import utils
from .websockets import AddressBalanceWs, BlockWebSocket
from .connector import Config
from .constants import COIN_SYMBOL


@CurrencyHandler
class Handler:

    def __init__(self, coin):
        self._coin = coin
        self._networksConfig = {}

    def addConfig(self, network, config):

        if network in self.networksConfig:
            logger.printError(f"Configuration {network} already added for {self.coin}")
            return False, f"Configuration {network} already added for {self.coin}"

        defaultConf, err = utils.loadDefaultPackageConf(self.coin)
        if err is not None:
            return False, err

        self.networksConfig[network] = Config(
            networkName=network,
            config={
                "bitcoincoreProtocol": config["bitcoincoreProtocol"] if "bitcoincoreProtocol" in config
                else defaultConf["bitcoincoreProtocol"],
                "bitcoincoreHost": config["bitcoincoreHost"] if "bitcoincoreHost" in config
                else defaultConf["bitcoincoreHost"],
                "bitcoincorePort": config["bitcoincorePort"] if "bitcoincorePort" in config
                else defaultConf["bitcoincorePort"],
                "bitcoincoreUser": config["bitcoincoreUser"] if "bitcoincoreUser" in config
                else defaultConf["bitcoincoreUser"],
                "bitcoincorePassword": config["bitcoincorePassword"] if "bitcoincorePassword" in config
                else defaultConf["bitcoincorePassword"],
                "bitcoincoreZmqProtocol": config["bitcoincoreZmqProtocol"] if "bitcoincoreZmqProtocol" in config
                else defaultConf["bitcoincoreZmqProtocol"],
                "bitcoincoreZmqPort": config["bitcoincoreZmqPort"] if "bitcoincoreZmqPort" in config
                else defaultConf["bitcoincoreZmqPort"],
                "bitcoincoreCallbackProtocol": config["bitcoincoreCallbackProtocol"] if "bitcoincoreCallbackProtocol" in config
                else defaultConf["bitcoincoreCallbackProtocol"],
                "bitcoincoreCallbackHost": config["bitcoincoreCallbackHost"] if "bitcoincoreCallbackHost" in config
                else defaultConf["bitcoincoreCallbackHost"],
                "electrumProtocol": config["electrumProtocol"] if "electrumProtocol" in config
                else defaultConf["electrumProtocol"],
                "electrumHost": config["electrumHost"] if "electrumHost" in config
                else defaultConf["electrumHost"],
                "electrumPort": config["electrumPort"] if "electrumPort" in config
                else defaultConf["electrumPort"],
                "electrumUser": config["electrumUser"] if "electrumUser" in config
                else defaultConf["electrumUser"],
                "electrumPassword": config["electrumPassword"] if "electrumPassword" in config
                else defaultConf["electrumPassword"]
            }
        )

        AddressBalanceWs(
            coin=self.coin,
            config=self.networksConfig[network]
        )
        BlockWebSocket(
            coin=self.coin,
            config=self.networksConfig[network]
        )

        websocket.startWebSockets(
            coin=self.coin,
            networkName=network
        )

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

        await websocket.stopWebSockets(
            coin=self.coin,
            networkName=network
        )

        # TODO: Check why it is not possible to return None in async function
        return True, ""

    async def updateConfig(self, network, config):

        if network not in self.networksConfig:
            logger.printError(f"Configuration {network} not added for {self.coin}")
            return False, f"Configuration {network} not added for {self.coin}"

        defaultConf, err = utils.loadDefaultPackageConf(self.coin)
        if err is not None:
            return False, err

        self.networksConfig[network] = Config(
            networkName=network,
            config={
                "bitcoincoreProtocol": config["bitcoincoreProtocol"] if "bitcoincoreProtocol" in config
                else defaultConf["bitcoincoreProtocol"],
                "bitcoincoreHost": config["bitcoincoreHost"] if "bitcoincoreHost" in config
                else defaultConf["bitcoincoreHost"],
                "bitcoincorePort": config["bitcoincorePort"] if "bitcoincorePort" in config
                else defaultConf["bitcoincorePort"],
                "bitcoincoreUser": config["bitcoincoreUser"] if "bitcoincoreUser" in config
                else defaultConf["bitcoincoreUser"],
                "bitcoincorePassword": config["bitcoincorePassword"] if "bitcoincorePassword" in config
                else defaultConf["bitcoincorePassword"],
                "bitcoincoreZmqProtocol": config["bitcoincoreZmqProtocol"] if "bitcoincoreZmqProtocol" in config
                else defaultConf["bitcoincoreZmqProtocol"],
                "bitcoincoreZmqPort": config["bitcoincoreZmqPort"] if "bitcoincoreZmqPort" in config
                else defaultConf["bitcoincoreZmqPort"],
                "bitcoincoreCallbackProtocol": config["bitcoincoreCallbackProtocol"] if "bitcoincoreCallbackProtocol" in config
                else defaultConf["bitcoincoreCallbackProtocol"],
                "bitcoincoreCallbackHost": config["bitcoincoreCallbackHost"] if "bitcoincoreCallbackHost" in config
                else defaultConf["bitcoincoreCallbackHost"],
                "electrumProtocol": config["electrumProtocol"] if "electrumProtocol" in config
                else defaultConf["electrumProtocol"],
                "electrumHost": config["electrumHost"] if "electrumHost" in config
                else defaultConf["electrumHost"],
                "electrumPort": config["electrumPort"] if "electrumPort" in config
                else defaultConf["electrumPort"],
                "electrumUser": config["electrumUser"] if "electrumUser" in config
                else defaultConf["electrumUser"],
                "electrumPassword": config["electrumPassword"] if "electrumPassword" in config
                else defaultConf["electrumPassword"]
            }
        )

        await websocket.stopWebSockets(
            coin=self.coin,
            networkName=network
        )

        AddressBalanceWs(
            coin=self.coin,
            config=self.networksConfig[network]
        )
        BlockWebSocket(
            coin=self.coin,
            config=self.networksConfig[network]
        )

        websocket.startWebSockets(
            coin=self.coin,
            networkName=network
        )

        # TODO: Check why it is not possible to return None in async function
        return True, ""

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
