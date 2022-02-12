#!/usr/bin/python
from httputils.router import CurrencyHandler
from httputils import httpmethod
from rpcutils import rpcmethod, rpcutils, error
from logger import logger
from utils import utils
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

        defaultConfig, err = utils.loadDefaultPackageConf(self.coin)
        if err is not None:
            return False, err

        self._networksConfig[network] = Config(
            networkName=network,
            config={
                "protocol": config["protocol"] if "protocol" in config else defaultConfig["protocol"],
                "host": config["host"] if "host" in config else defaultConfig["host"],
                "rpcPort": config["rpcPort"] if "rpcPort" in config else defaultConfig["rpcPort"],
                "rpcPath": config["rpcPath"] if "rpcPath" in config else defaultConfig["rpcPath"]
            }
        )

        return True, None

    def getConfig(self, network):

        if network not in self.networksConfig:
            logger.printError(f"Configuration {network} not added for {self.coin}")
            return None, f"Configuration {network} not added for {self.coin}"

        return self.networksConfig[network].jsonEncode(), None

    def removeConfig(self, network):

        if network not in self.networksConfig:
            logger.printError(f"Configuration {network} not added for {self.coin}")
            return False, f"Configuration {network} not added for {self.coin}"

        del self.networksConfig[network]

        return True, None

    def updateConfig(self, network, config):

        if network not in self.networksConfig:
            logger.printError(f"Configuration {network} not added for {self.coin}")
            return False, f"Configuration {network} not added for {self.coin}"

        defaultConfig, err = utils.loadDefaultPackageConf(self.coin)
        if err is not None:
            return False, err

        self.networksConfig[network] = Config(
            networkName=network,
            config={
                "protocol": config["protocol"] if "protocol" in config else defaultConfig["protocol"],
                "host": config["host"] if "host" in config else defaultConfig["host"],
                "rpcPort": config["rpcPort"] if "rpcPort" in config else defaultConfig["rpcPort"],
                "wsPort": config["wsPort"] if "wsPort" in config else defaultConfig["wsPort"]
            }
        )

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

    @property
    def coin(self):
        return self._coin

    @property
    def networksConfig(self):
        return self._networksConfig

    @coin.setter
    def coin(self, value):
        self._coin = value

    @networksConfig.setter
    def networksConfig(self, value):
        self._networksConfig = value


Handler(COIN_SYMBOL)
