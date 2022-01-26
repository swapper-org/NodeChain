#!/usr/bin/python
from httputils.router import CurrencyHandler
from rpcutils import rpcutils
from utils import utils
from logger import logger
from .connector import Config
from httputils import httpmethod
from rpcutils import rpcmethod, error


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

        self.networksConfig[network] = Config(
            config={
                "protocol": config["protocol"] if "protocol" in config else defaultConfig["protocol"],
                "host": config["host"] if "host" in config else defaultConfig["host"],
                "rpcPort": config["rpcPort"] if "rpcPort" in config else defaultConfig["rpcPort"],
                "wsPort": config["wsPort"] if "wsPort" in config else defaultConfig["wsPort"]
            }
        )
        return True, None

        # TODO: Init websockets and everything related to the pkg

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
        # TODO: Close websockets and everything related to the pkg

    def updateConfig(self, network, config):

        if network not in self.networksConfig:
            logger.printError(f"Configuration {network} not added for {self.coin}")
            return False, f"Configuration {network} not added for {self.coin}"

        defaultConfig, err = utils.loadDefaultPackageConf(self.coin)
        if err is not None:
            return False, err

        self.networksConfig[network] = Config(
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
            return rpcmethod.callMethod(
                coin=self.coin,
                request=request,
                config=self.networksConfig[network]
            )
        else:
            try:
                return httpmethod.callMethod(
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
