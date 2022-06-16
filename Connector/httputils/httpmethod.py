#!/usr/bin/python
import sys
import random
from logger import logger
from . import error, httputils
from .constants import GET_METHOD, POST_METHOD


callbackMethods = {}


class HTTPMethod:

    def __init__(self, type, handler):

        self.type = type
        self.handlerName = handler.__name__
        self.handler = handler


class RouteTableDef:

    httpMethods = {}

    @staticmethod
    def _isWrapperApiRegistered(wrapperApiId):

        return wrapperApiId in RouteTableDef.httpMethods

    @staticmethod
    def _isMethodRegistered(wrapperApiId, methodName):

        if not RouteTableDef._isWrapperApiRegistered(wrapperApiId=wrapperApiId):
            return False

        return methodName in RouteTableDef.httpMethods[wrapperApiId]

    @staticmethod
    def _isAvailableMethodType(wrapperApiId, methodName, methodType):

        if not RouteTableDef._isMethodRegistered(wrapperApiId=wrapperApiId, methodName=methodName):
            return False

        return RouteTableDef.httpMethods[wrapperApiId][methodName].type == methodType

    @staticmethod
    def _registerMethod(wrapperApiId, methodName, httpMethod):

        if not RouteTableDef._isWrapperApiRegistered(wrapperApiId=wrapperApiId):
            logger.printInfo(f"Registering new HTTP method {methodName} for wrapper API {wrapperApiId}")
            RouteTableDef.httpMethods[wrapperApiId] = {methodName: httpMethod}

        elif not RouteTableDef._isMethodRegistered(wrapperApiId=wrapperApiId, methodName=methodName):
            logger.printInfo(f"Registering new HTTP method {methodName} for wrapper API {wrapperApiId}")
            RouteTableDef.httpMethods[wrapperApiId][methodName] = httpMethod

        else:
            logger.printError(f"HTTP Method {methodName} already registered for wrapper API {wrapperApiId}")

    @staticmethod
    def get(currency, standard=None):

        wrapperApiId = currency if standard is None else f"{currency}/{standard}"

        def _get(function):

            async def wrapper(request, config):

                return await function(
                    random.randint(0, sys.maxsize),
                    request,
                    config
                )

            RouteTableDef._registerMethod(
                wrapperApiId=wrapperApiId,
                methodName=function.__name__,
                httpMethod=HTTPMethod(
                    type=GET_METHOD,
                    handler=wrapper
                )
            )

            return function

        return _get

    @staticmethod
    def post(currency, standard=None):

        wrapperApiId = currency if standard is None else f"{currency}/{standard}"

        def _post(function):

            async def wrapper(request, config):

                return await function(
                    random.randint(0, sys.maxsize),
                    request,
                    config
                )

            RouteTableDef._registerMethod(
                wrapperApiId=wrapperApiId,
                methodName=function.__name__,
                httpMethod=HTTPMethod(
                    type=POST_METHOD,
                    handler=wrapper
                )
            )

            return function

        return _post

    @staticmethod
    async def callMethod(coin, method, request, config, standard=None):

        wrapperApiId = coin if standard is None else f"{coin}/{standard}"

        if not RouteTableDef._isMethodRegistered(wrapperApiId=wrapperApiId, methodName=method):
            raise error.NotFoundError("Not found")
        elif not RouteTableDef._isAvailableMethodType(wrapperApiId=wrapperApiId, methodName=method, methodType=request.method):
            raise error.MethodNotAllowedError("Method not allowed")

        payload = httputils.parseJSONRequest(await request.read()) if not httputils.isGetMethod(request.method) else {}
        return await RouteTableDef.httpMethods[wrapperApiId][method].handler(payload, config)


def callbackMethod(callbackName, coin, standard=None):

    wrapperApiId = coin if standard is None else f"{coin}/{standard}"

    def _callbackMethod(function):

        def wrapper(request, config):

            return function(
                request=request,
                config=config,
                coin=coin
            )

        if wrapperApiId not in callbackMethods:
            logger.printInfo(f"Registering new callback method {callbackName} for wrapper API {wrapperApiId}")
            callbackMethods[wrapperApiId] = {callbackName: wrapper}

        elif callbackName not in callbackMethods[coin]:
            logger.printInfo(f"Registering new callback method {callbackName} for wrapper API {wrapperApiId}")
            callbackMethods[wrapperApiId][callbackName] = wrapper

        else:
            logger.printError(f"callback Method {callbackName} already registered for wrapper API {wrapperApiId}")

        return function

    return _callbackMethod


async def callCallbackMethod(coin, callbackName, request, config, standard=None):

    payload = httputils.parseJSONRequest(await request.read())
    wrapperApiId = coin if standard is None else f"{coin}/{standard}"

    if wrapperApiId not in callbackMethods:
        raise error.NotFoundError("Wrapper API not supported")
    if callbackName not in callbackMethods[coin]:
        raise error.NotFoundError("Method not found for  wrapper API")

    return callbackMethods[wrapperApiId][callbackName](payload, config)
