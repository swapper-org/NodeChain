#!/usr/bin/python
from httputils import httputils
from logger.logger import Logger
from . import rpcutils, error
from .constants import *


class RPCMethod:

    def __init__(self, type, handler):

        self.type = type
        self.handlerName = handler.__name__
        self.handler = handler


class RouteTableDef:

    rpcMethods = {}

    @staticmethod
    def _isWrapperApiRegistered(wrapperApiId):

        return wrapperApiId in RouteTableDef.rpcMethods

    @staticmethod
    def _isMethodRegistered(wrapperApiId, methodName):

        if not RouteTableDef._isWrapperApiRegistered(wrapperApiId=wrapperApiId):
            return False

        return methodName in RouteTableDef.rpcMethods[wrapperApiId]

    @staticmethod
    def _isAvailableMethodType(wrapperApiId, methodName, methodType):

        if not RouteTableDef._isMethodRegistered(wrapperApiId=wrapperApiId, methodName=methodName):
            return False

        return RouteTableDef.rpcMethods[wrapperApiId][methodName].type == methodType

    @staticmethod
    def _registerMethod(wrapperApiId, methodName, rpcMethod):

        if not RouteTableDef._isWrapperApiRegistered(wrapperApiId=wrapperApiId):
            Logger.printDebug(f"Registering new RPC method {methodName} for wrapper API {wrapperApiId}")
            RouteTableDef.rpcMethods[wrapperApiId] = {methodName: rpcMethod}

        elif not RouteTableDef._isMethodRegistered(wrapperApiId=wrapperApiId, methodName=methodName):
            Logger.printDebug(f"Registering new RPC method {methodName} for wrapper API {wrapperApiId}")
            RouteTableDef.rpcMethods[wrapperApiId][methodName] = rpcMethod

        else:
            Logger.printError(f"HTTP Method {methodName} already registered for wrapper API {wrapperApiId}")

    @staticmethod
    def rpc(currency, standard=None):

        wrapperApiId = currency if standard is None else f"{currency}/{standard}"

        def _rpc(function):

            async def wrapper(request, config):

                response = await function(
                    request[ID],
                    request[PARAMS],
                    config
                )
                return {
                    ID: request[ID],
                    JSON_RPC: JSON_RPC_VERSION,
                    RESULT: response
                }

            RouteTableDef._registerMethod(
                wrapperApiId=wrapperApiId,
                methodName=function.__name__,
                rpcMethod=RPCMethod(
                    type=POST_METHOD,
                    handler=wrapper
                )
            )

            return function

        return _rpc

    @staticmethod
    async def callMethod(coin, config, request, standard=None):

        payload = httputils.parseJSONRequest(await request.read())
        rpcPayload = rpcutils.parseJsonRpcRequest(payload)
        wrapperApiId = coin if standard is None else f"{coin}/{standard}"

        if not RouteTableDef._isMethodRegistered(wrapperApiId=wrapperApiId, methodName=rpcPayload[METHOD]):
            raise error.RpcNotFoundError(id=rpcPayload[ID])
        elif not RouteTableDef._isAvailableMethodType(
                wrapperApiId=wrapperApiId,
                methodName=rpcPayload[METHOD],
                methodType=request.method
        ):
            raise error.RpcMethodNotAllowedError(id=rpcPayload["id"])

        return await RouteTableDef.rpcMethods[wrapperApiId][payload[METHOD]].handler(rpcPayload, config)
