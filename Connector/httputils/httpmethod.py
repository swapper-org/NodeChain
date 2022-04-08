#!/usr/bin/python
import sys
import random
from logger import logger
from . import error, httputils

httpMethods = {}
callbackMethods = {}


def callbackMethod(callbackName, coin, standard=None):

    wrappreApiId = coin if standard is None else f"{coin}/{standard}"

    def _callbackMethod(function):

        def wrapper(request, config):

            return function(
                request=request,
                config=config,
                coin=coin
            )

        if wrappreApiId not in callbackMethods:
            logger.printInfo(f"Registering new callback method {callbackName} for wrapper API {wrappreApiId}")
            callbackMethods[wrappreApiId] = {callbackName: wrapper}

        elif callbackName not in callbackMethods[coin]:
            logger.printInfo(f"Registering new callback method {callbackName} for wrapper API {wrappreApiId}")
            callbackMethods[wrappreApiId][callbackName] = wrapper

        else:
            logger.printError(f"callback Method {callbackName} already registered for wrapper API {wrappreApiId}")

        return function

    return _callbackMethod


def httpMethod(coin, standard=None):

    wrapperApiId = coin if standard is None else f"{coin}/{standard}"

    def _httpMethod(function):

        def wrapper(request, config):

            return function(
                random.randint(0, sys.maxsize),
                request,
                config
            )

        if wrapperApiId not in httpMethods:
            logger.printInfo(f"Registering new HTTP method {function.__name__} for wrapper API {wrapperApiId}")
            httpMethods[wrapperApiId] = {function.__name__: wrapper}

        elif function.__name__ not in httpMethods[wrapperApiId]:
            logger.printInfo(f"Registering new HTTP method {function.__name__} for wrapper API {wrapperApiId}")
            httpMethods[wrapperApiId][function.__name__] = wrapper

        else:
            logger.printError(f"HTTP Method {function.__name__} already registered for wrapper API {wrapperApiId}")

        return function

    return _httpMethod


async def callMethod(coin, method, request, config, standard=None):

    payload = httputils.parseJSONRequest(await request.read()) if not httputils.isGetMethod(request.method) else {}
    wrapperApiId = coin if standard is None else f"{coin}/{standard}"

    if wrapperApiId not in httpMethods:
        raise error.BadRequestError(f"Calling {wrapperApiId} method when wrapper API is not supported")
    if method not in httpMethods[wrapperApiId]:
        raise error.BadRequestError(f"Calling unknown method {method} for wrapper API {wrapperApiId}")

    return httpMethods[wrapperApiId][method](payload, config)


async def callCallbackMethod(coin, callbackName, request, config, standard=None):

    payload = httputils.parseJSONRequest(await request.read())
    wrapperApiId = coin if standard is None else f"{coin}/{standard}"

    if wrapperApiId not in callbackMethods:
        raise error.BadRequestError(f"Calling {wrapperApiId} method when wrapper API is not supported")
    if callbackName not in callbackMethods[coin]:
        raise error.BadRequestError(f"Calling unknown method {callbackName} for wrapper API {wrapperApiId}")

    return callbackMethods[wrapperApiId][callbackName](payload, config)
