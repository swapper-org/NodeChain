#!/usr/bin/python
import sys
import random
from . import error
from logger import logger

postHttpMethods = {}


def postHttpMethod(coin):

    def _postHttpMethod(function):

        def wrapper(request, config):

            return function(
                random.randint(0, sys.maxsize),
                request,
                config
            )

        if coin not in postHttpMethods:
            logger.printInfo(f"Registering new HTTP method {function.__name__} for currency {coin}")
            postHttpMethods[coin] = {function.__name__: wrapper}

        elif function.__name__ not in postHttpMethods[coin]:
            logger.printInfo(f"Registering new HTTP method {function.__name__} for currency {coin}")
            postHttpMethods[coin][function.__name__] = wrapper

        else:
            logger.printError(f"HTTP Method {function.__name__} already registered for currency {coin}")

        return function

    return _postHttpMethod


def callMethod(coin, method, request, config):

    if coin not in postHttpMethods:
        raise error.BadRequestError(f"Calling {coin} method when currency is not supported")
    if method not in postHttpMethods[coin]:
        raise error.BadRequestError(f"Calling unknown method {method} for currency {coin}")

    return postHttpMethods[coin][method](request, config)
