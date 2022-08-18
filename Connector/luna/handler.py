#!/usr/bin/python
from httputils.router import CurrencyHandler
from httputils import httpmethod
from rpcutils import rpcmethod, error
from logger.logger import Logger
from .config import Config
from .constants import COIN_SYMBOL


@CurrencyHandler
class Handler:

    def __init__(self, coin):
        self._coin = coin
        self._networksConfig = {}

    def addConfig(self, network, config):

        if network in self.networksConfig:
            Logger.printDebug(f"Configuration {network} already added for {self.coin}")
            return False, "Configuration already added"

        pkgConfig = Config(
            coin=self.coin,
            networkName=network
        )

        ok, err = pkgConfig.loadConfig(config=config)
        if not ok:
            Logger.printError(f"Can not load config for {network} for {self.coin}: {err}")
            return ok, err

        self.networksConfig[network] = pkgConfig

        return True, None

    def getConfig(self, network):

        if network not in self.networksConfig:
            Logger.printDebug(f"Configuration {network} not added for {self.coin}")
            return None, "Configuration not added"

        return self.networksConfig[network].jsonEncode(), None

    async def removeConfig(self, network):

        if network not in self.networksConfig:
            Logger.printDebug(f"Configuration {network} not added for {self.coin}")
            return False, "Configuration not added"

        del self.networksConfig[network]

        return True, None

    async def updateConfig(self, network, config):

        if network not in self.networksConfig:
            Logger.printDebug(f"Configuration {network} not added for {self.coin}")
            return False, "Configuration not added"

        ok, err = self.networksConfig[network].loadConfig(config=config)
        if not ok:
            Logger.printError(f"Can not load config for {network} for {self.coin}: {err}")
            return ok, err

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
