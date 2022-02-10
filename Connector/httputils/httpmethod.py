#!/usr/bin/python
import sys
import random
from logger import logger
from . import error, httputils

postHttpMethods = {}
callbackMethods = {}


def callbackMethod(callbackName, coin):

    def _callbackMethod(function):

        def wrapper(request, config):

            return function(
                request=request,
                config=config,
                coin=coin
            )

        if coin not in callbackMethods:
            logger.printInfo(f"Registering new callback method {callbackName} for currency {coin}")
            callbackMethods[coin] = {callbackName: wrapper}

        elif callbackName not in callbackMethods[coin]:
            logger.printInfo(f"Registering new callback method {callbackName} for currency {coin}")
            callbackMethods[coin][callbackName] = wrapper

        else:
            logger.printError(f"callback Method {callbackName} already registered for currency {coin}")

        return function
    return _callbackMethod


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


async def callMethod(coin, method, request, config):

    payload = httputils.parseJSONRequest(await request.read())

    if coin not in postHttpMethods:
        raise error.BadRequestError(f"Calling {coin} method when currency is not supported")
    if method not in postHttpMethods[coin]:
        raise error.BadRequestError(f"Calling unknown method {method} for currency {coin}")

    return postHttpMethods[coin][method](payload, config)


async def callCallbackMethod(coin, callbackName, request, config):

    payload = httputils.parseJSONRequest(await request.read())

    if coin not in callbackMethods:
        raise error.BadRequestError(f"Calling {coin} method when currency is not supported")
    if callbackName not in callbackMethods[coin]:
        raise error.BadRequestError(f"Calling unknown method {callbackName} for currency {coin}")

    return callbackMethods[coin][callbackName](payload, config)
