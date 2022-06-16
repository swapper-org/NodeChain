#!/usr/bin/python
import aiohttp
from logger import logger
from httputils import httputils, error as httpError
from rpcutils import rpcutils, error
from rpcutils.constants import *
from . import subscribers, broker


class WSMethod:

    def __init__(self, handler):
        self.handlerName = handler.__name__
        self.handler = handler


class RouteTableDef:

    wsMethods = {}

    @staticmethod
    def _isWrapperApiRegistered(wrapperApiId):

        return wrapperApiId in RouteTableDef.wsMethods

    @staticmethod
    def _isMethodRegistered(wrapperApiId, methodName):

        if not RouteTableDef._isWrapperApiRegistered(wrapperApiId=wrapperApiId):
            return False

        return methodName in RouteTableDef.wsMethods[wrapperApiId]

    @staticmethod
    def _isAvailableMethodType(wrapperApiId, methodName, methodType):

        if not RouteTableDef._isMethodRegistered(wrapperApiId=wrapperApiId, methodName=methodName):
            return False

        return RouteTableDef.wsMethods[wrapperApiId][methodName].type == methodType

    @staticmethod
    def _registerMethod(wrapperApiId, methodName, wsMethod):

        if not RouteTableDef._isWrapperApiRegistered(wrapperApiId=wrapperApiId):
            logger.printInfo(f"Registering new WS method {methodName} for wrapper API {wrapperApiId}")
            RouteTableDef.wsMethods[wrapperApiId] = {methodName: wsMethod}

        elif not RouteTableDef._isMethodRegistered(wrapperApiId=wrapperApiId, methodName=methodName):
            logger.printInfo(f"Registering new WS method method {methodName} for wrapper API {wrapperApiId}")
            RouteTableDef.wsMethods[wrapperApiId][methodName] = wsMethod

        else:
            logger.printError(f"WS Method {methodName} already registered for wrapper API {wrapperApiId}")

    @staticmethod
    def ws(currency, standard=None):

        wrapperApiId = currency if standard is None else f"{currency}/{standard}"

        def _ws(function):

            async def wrapper(subscriber, rpcPayload, config):

                return await function(subscriber, rpcPayload[ID], rpcPayload[PARAMS], config)

            RouteTableDef._registerMethod(
                wrapperApiId=wrapperApiId,
                methodName=function.__name__,
                wsMethod=WSMethod(
                    handler=wrapper
                )
            )

            return function

        return _ws

    @staticmethod
    async def callMethod(coin, config, request):

        subscriber = subscribers.WSSubscriber()
        await subscriber.websocket.prepare(request=request)
        broker.Broker().register(subscriber)
        payload = None

        try:

            async for msg in subscriber.websocket:

                if msg.type == aiohttp.WSMsgType.TEXT:
                    payload = httputils.parseJSONRequest(msg.data)
                    rpcPayload = rpcutils.parseJsonRpcRequest(payload)

                    if rpcPayload[METHOD] == "close":
                        await subscriber.sendMessage(
                            rpcutils.generateRPCResultResponse(
                                rpcPayload[rpcutils.ID] if rpcutils is not None else rpcutils.UNKNOWN_RPC_REQUEST_ID,
                                "Connection closed with server"
                            )
                        )
                        await subscriber.close(broker.Broker())

                    elif coin not in RouteTableDef.wsMethods or rpcPayload[METHOD] not in RouteTableDef.wsMethods[coin]:
                        raise error.RpcNotFoundError(
                            id=rpcPayload[ID],
                            message="Not found"
                        )

                    else:
                        response = await RouteTableDef.wsMethods[coin][rpcPayload[METHOD]].handler(
                            subscriber,
                            rpcPayload,
                            config
                        )
                        rpcResponse = rpcutils.generateRPCResultResponse(
                            id=rpcPayload[ID],
                            params=response
                        )
                        logger.printInfo(f"Sending WS response to requestor: {rpcResponse}")

                        await subscriber.sendMessage(rpcResponse)

                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.printError('WS connection closed with exception %s' % subscriber.websocket.exception())
                    raise error.RpcInternalServerError(
                        id=-1,
                        message='WS connection closed with exception %s' % subscriber.websocket.exception()
                    )

        except error.RpcError as err:
            response = rpcutils.generateRPCResultResponse(
                payload[rpcutils.ID] if payload is not None else rpcutils.UNKNOWN_RPC_REQUEST_ID,
                err.jsonEncode()
            )

            logger.printError(f"Sending RPC error response to requester: {response}")

            await subscriber.sendMessage(response)
            await subscriber.close(broker.Broker())

        except httpError.Error as err:
            response = rpcutils.generateRPCResultResponse(
                payload[rpcutils.ID] if payload is not None else rpcutils.UNKNOWN_RPC_REQUEST_ID,
                err.jsonEncode()
            )

            logger.printError(f"Sending RPC http response to requester: {response}")

            await subscriber.sendMessage(response)
            await subscriber.close(broker.Broker())
        finally:
            broker.Broker().unregister(subscriber)

        return subscriber.websocket
