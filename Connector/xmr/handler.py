#!/usr/bin/python
from httputils.router import CurrencyHandler
from httputils import httpmethod
from rpcutils import rpcmethod, rpcutils, error
from logger import logger
from utils import utils
from .config import Config
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

        pkgConfig = Config(
            coin=self.coin,
            networkName=network
        )

        ok, err = pkgConfig.loadConfig(config=config)
        if not ok:
            logger.printError(f"Can not load config for {network} for {self.coin}: {err}")
            return ok, err

        self.networksConfig[network] = pkgConfig

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

        return True, None

    async def updateConfig(self, network, config):

        if network not in self.networksConfig:
            logger.printError(f"Configuration {network} not added for {self.coin}")
            return False, f"Configuration {network} not added for {self.coin}"

        ok, err = self.networksConfig[network].loadConfig(config=config)
        if not ok:
            logger.printError(f"Can not load config for {network} for {self.coin}: {err}")
            return ok, err

        return True, None

    async def handleRPCRequest(self, network, standard, request):

        return await rpcmethod.callMethod(
            coin=self.coin,
            standard=standard,
            request=request,
            config=self.networksConfig[network]
        )

    async def handleHTTPRequest(self, network, standard, method, request):
        try:
            return await httpmethod.callMethod(
                coin=self.coin,
                standard=standard,
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
