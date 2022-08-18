#!/usr/bin/python
from aiohttp import web
import json
from logger.logger import Logger
from patterns import Singleton
from utils import utils
from . import error

currenciesHandler = {}


class Router(object, metaclass=Singleton.Singleton):

    def __init__(self):
        self._availableCoins = {}

    async def doRPCRoute(self, request):

        coin = request.match_info["coin"]
        network = request.match_info["network"]

        standard = None
        try:
            standard = request.match_info["standard"]
        except KeyError:
            pass

        self.checkIsAvailableRoute(
            coin=coin,
            network=network
        )

        response = await currenciesHandler[coin].handleRPCRequest(
            network=network,
            standard=standard,
            request=request
        )

        return web.Response(
            text=json.dumps(response)
        )

    async def doHTTPRoute(self, request):

        coin = request.match_info["coin"]
        network = request.match_info["network"]
        method = request.match_info["method"]

        standard = None
        try:
            standard = request.match_info["standard"]
        except KeyError:
            pass

        self.checkIsAvailableRoute(
            coin=coin,
            network=network
        )

        response = await currenciesHandler[coin].handleHTTPRequest(
            network=network,
            standard=standard,
            method=method,
            request=request
        )

        return web.Response(
            text=json.dumps(response)
        )

    async def doWsRoute(self, request):

        coin = request.match_info["coin"]
        network = request.match_info["network"]

        self.checkIsAvailableRoute(
            coin=coin,
            network=network
        )

        coinHandler = currenciesHandler[coin]
        return await coinHandler.handleWsRequest(
            network=network,
            request=request
        )

    async def handleCallback(self, request):

        coin = request.match_info["coin"]
        network = request.match_info["network"]
        callbackName = request.match_info["callbackName"]

        self.checkIsAvailableRoute(
            coin=coin,
            network=network
        )

        coinHandler = currenciesHandler[coin]
        response = await coinHandler.handleCallback(
            network=network,
            callbackName=callbackName,
            request=request
        )

        return web.Response(
            text=json.dumps(response)
        )

    async def addCoin(self, coin, network, config):

        ok, err = self.checkCoinNetworkIntegrity(coin=coin, network=network)
        if not ok:
            return {
                "success": False,
                "message": err
            }

        if coin in self._availableCoins and network in self._availableCoins[coin]:
            Logger.printError(f"Can not add {network} network for {coin} because it is already added")
            return {
                "success": False,
                "message": "Network already registered"
            }

        coinHandler = currenciesHandler[coin]
        ok, err = await coinHandler.addConfig(network=network, config=config)
        if not ok:
            return {
                "success": False,
                "message": err
            }

        if coin not in self._availableCoins:
            self._availableCoins[coin] = {
                network: None
            }
        else:
            self._availableCoins[coin][network] = None

        return {
            "success": True,
            "message": "Network added successfully"
        }

    async def removeCoin(self, coin, network):

        ok, err = self.checkCoinNetworkIntegrity(coin=coin, network=network)
        if not ok:
            return {
                "success": False,
                "message": err
            }

        try:
            self.checkIsAvailableRoute(coin=coin, network=network)
        except error.NotFoundError:
            Logger.printError(f"{network} network has not been previously added for currency {coin}")
            return {
                "success": False,
                "message": "Can not remove network"
            }

        Logger.printDebug(f"Removing {network} network for currency {coin}")

        del self._availableCoins[coin][network]
        if len(self._availableCoins[coin]) == 0:
            del self._availableCoins[coin]

        coinHandler = currenciesHandler[coin]
        ok, err = await coinHandler.removeConfig(network)

        return {
            "success": ok,
            "message": "Network added successfully" if ok else err
        }

    def getCoin(self, coin, network):

        ok, err = self.checkCoinNetworkIntegrity(coin=coin, network=network)
        if not ok:
            return {
                "success": False,
                "message": err
            }

        try:
            self.checkIsAvailableRoute(coin=coin, network=network)
        except error.NotFoundError:
            Logger.printError(f"{network} network has not been previously added for currency {coin}")
            return {
                "success": False,
                "message": "Can not get network configuration"
            }

        Logger.printDebug(f"Returning configuration for {network} network for currency {coin}")

        coinHandler = currenciesHandler[coin]
        config, err = coinHandler.getConfig(network)
        if err is not None:
            return {
                "success": False,
                "message": err
            }

        return {
            "success": True,
            "message": "Configuration for network for currency retrieved successfully",
            "coin": coin,
            "network": network,
            "config": config
        }

    async def updateCoin(self, coin, network, config):

        ok, err = self.checkCoinNetworkIntegrity(coin=coin, network=network)
        if not ok:
            return {
                "success": False,
                "message": err
            }

        try:
            self.checkIsAvailableRoute(coin=coin, network=network)
        except error.NotFoundError:
            Logger.printError(f"{network} network has not been previously added for currency {coin}")
            return {
                "success": False,
                "message": "Can not update network configuration"
            }

        Logger.printInfo(f"Updating configuration for network {network} for currency {coin}")

        coinHandler = currenciesHandler[coin]
        ok, err = await coinHandler.updateConfig(network, config)

        return {
            "success": ok,
            "message": "Configuration network updated successfully" if ok else err
        }

    def checkIsAvailableRoute(self, coin, network):

        if coin not in self._availableCoins:
            Logger.printError(f"Currency {coin} has not been previously added")
            raise error.NotFoundError()

        if network not in self._availableCoins[coin]:
            Logger.printError(f"{network} network for {coin} has not been previously added")
            raise error.NotFoundError()

    def checkCoinNetworkIntegrity(self, coin, network):

        if not utils.isAvailableCurrency(coin):
            Logger.printError(f"Currency {coin} is not supported")
            return False, "Currency not supported"

        if not utils.isAvailableNetworkForCurrency(coin, network):
            Logger.printError(f"{network} network not supported for currency {coin}")
            return False, "Network not supported for currency"

        return True, ""


class CurrencyHandler:

    def __init__(self, handler):
        self.handler = handler

    def __call__(self, coin):

        def addConfig(network, config):
            pass

        def getConfig(network):
            pass

        def removeConfig(network):
            pass

        def updateConfig(network, config):
            pass

        async def handleRequest(network, method, request):
            pass

        async def handleWsRequest(network, request):
            pass

        def handleCallback(network, callbackName, request):
            pass

        self.handler.addConfig = addConfig \
            if not hasattr(self.handler, "addConfig") or not callable(self.handler.addConfig) \
            else self.handler.addConfig

        self.handler.getConfig = getConfig \
            if not hasattr(self.handler, "getConfig") or not callable(self.handler.getConfig) \
            else self.handler.getConfig

        self.handler.removeConfig = removeConfig \
            if not hasattr(self.handler, "removeConfig") or not callable(self.handler.removeConfig) \
            else self.handler.removeConfig

        self.handler.updateConfig = updateConfig \
            if not hasattr(self.handler, "updateConfig") or not callable(self.handler.updateConfig) \
            else self.handler.updateConfig

        self.handler.handleRequest = handleRequest \
            if not hasattr(self.handler, "handleRequest") or not callable(self.handler.handleRequest) \
            else self.handler.handleRequest

        self.handler.handleWsRequest = handleWsRequest \
            if not hasattr(self.handler, "handleWsRequest") or not callable(self.handler.handleWsRequest) \
            else self.handler.handleWsRequest

        self.handler.handleCallback = handleCallback \
            if not hasattr(self.handler, "handleCallback") or not callable(self.handler.handleCallback) \
            else self.handler.handleCallback

        obj = self.handler(coin)
        currenciesHandler[coin] = obj

        return obj
