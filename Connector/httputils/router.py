#!/usr/bin/python
import asyncio
import json
from logger import logger
from patterns import Singleton
from utils import utils
from . import error


class Router(object, metaclass=Singleton.Singleton):

    def __init__(self):
        self._availableCoins = {}

    @asyncio.coroutine
    def doRoute(self, request):
        pass

    def addCoin(self, coin, network, config):

        if not self.isAvailableCurrency(coin):
            logger.printError(f"Currency {coin} is not supported")
            raise error.BadRequestError(f"Currency {coin} is not supported")

        if coin in self._availableCoins:
            if network in self._availableCoins[coin]:
                logger.printError(f"Can not add {network} network for {coin} because it is already added")
                return {
                    "success": False,
                    "message": f"Can not add {network} networrk for {coin} because it is already added"
                }

        if not self.isAvailableNetworkForCurrency(coin, network):
            logger.printError(f"{network} network not supported for currency {coin}")
            return {
                "success": False,
                "message": f"{network} network not supported for currency {coin}"
            }

        self._availableCoins[coin] = {
            network: {}
        }

        return {
            "success": True,
            "message": f"{network} network added for currency {coin}"
        }

    def removeCoin(self, coin, network):

        if not self.isAvailableCurrency(coin):
            logger.printError(f"Currency {coin} is not supported")
            raise error.BadRequestError(f"Currency {coin} is not supported")

        if coin not in self._availableCoins:
            logger.printError(f"Currency {coin} has not been previously added")
            return {
                "success": False,
                "message": f"Currency {coin} has not been previously added"
            }

        if network not in self._availableCoins[coin]:
            logger.printError(f"{network} network has not been previously added for currency {coin}")
            return {
                "success": False,
                "message": f"{network} network has not been previously added for currency {coin}"
            }

        logger.printInfo(f"Removing {network} network for currency {coin}")
        del self._availableCoins[coin][network]
        return {
            "success": True,
            "message": f"{network} network removed for currency {coin}"
        }

    def getCoin(self, coin, network):

        if not self.isAvailableCurrency(coin):
            logger.printError(f"Currency {coin} is not supported")
            raise error.BadRequestError(f"Currency {coin} is not supported")

        if coin not in self._availableCoins:
            logger.printError(f"Currency {coin} has not been previously added")
            return {
                "success": False,
                "message": f"Currency {coin} has not been previously added"
            }

        if network not in self._availableCoins[coin]:
            logger.printError(f"{network} network has not been previously added for currency {coin}")
            return {
                "success": False,
                "message": f"{network} network has not been previously added for currency {coin}"
            }

        logger.printInfo(f"Returning configuration for {network} network for currency {coin}")
        return {
            "success": True,
            "message": f"Config configuration for {network} network for currency {coin} retrieved successfully",
            "coin": coin,
            "network": network,
            "config": self._availableCoins[coin][network]
        }

    def updateCoin(self, coin, network, config):

        if not self.isAvailableCurrency(coin):
            logger.printError(f"Currency {coin} is not supported")
            raise error.BadRequestError(f"Currency {coin} is not supported")

        if coin not in self._availableCoins:
            logger.printError(f"Currency {coin} has not been previously added")
            return {
                "success": False,
                "message": f"Currency {coin} has not been previously added"
            }

        if network not in self._availableCoins[coin]:
            logger.printError(f"Network {network} has not been previously added for currency {coin}")
            return {
                "success": False,
                "message": f"Network {network} has not been previously added for currency {coin}"
            }

        logger.printInfo(f"Updating configuration for network {network} for currency {coin}")
        self._availableCoins[coin] = {
            network: {}
        }
        return {
            "success": True,
            "message": f"Configuration for {network} network for currency {coin} updated successfully"
        }

    def isAvailableCurrency(self, coin):

        availaCurrenciesFile = utils.getAvailableCurrenciesFile()

        try:

            with open(availaCurrenciesFile) as file:
                config = json.load(file)
                return coin in [conf["token"] for conf in config if "token" in conf]

        except FileNotFoundError as err:
            logger.printError(f"File {availaCurrenciesFile} could not be found")
            raise error.InternalServerError(f"File {availaCurrenciesFile} could not be found:{err}")

    def isAvailableNetworkForCurrency(self, coin, network):

        availaCurrenciesFile = utils.getAvailableCurrenciesFile()

        try:

            with open(availaCurrenciesFile) as file:
                config = json.load(file)

                for conf in config:
                    if "token" in conf and conf["token"] == coin:
                        if "networks" in conf:
                            return network in conf["networks"]

            return False

        except FileNotFoundError as err:
            logger.printError(f"File {availaCurrenciesFile} could not be found")
            raise error.InternalServerError(f"File {availaCurrenciesFile} could not be found:{err}")
