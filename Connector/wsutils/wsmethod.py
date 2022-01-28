#!/usr/bin/python
import aiohttp
from logger import logger
from httputils import httputils, error as httpError
from rpcutils import rpcutils, error
from rpcutils.constants import *
from . import subscribers, broker

wsMethods = {}


def wsMethod(coin):

    def _wsMethod(function):

        def wrapped(subscriber, rpcPayload, config):

            return function(subscriber, rpcPayload[ID], rpcPayload[PARAMS], config.networkName)

        if coin not in wsMethods:
            logger.printInfo(f"Registering new JSON WS method {function.__name__} for currency {coin}")
            wsMethods[coin] = {function.__name__: wrapped}

        elif function.__name__ not in wsMethods[coin]:
            logger.printInfo(f"Registering new JSON WS method {function.__name__} for currency {coin}")
            wsMethods[coin][function.__name__] = wrapped

        else:
            logger.printError(f"JSON WS Method {function.__name__} already registered for currency {coin}")

        return function

    return _wsMethod


async def callMethod(coin, config, request):

    subscriber = subscribers.WSSubscriber()
    await subscriber.websocket.prepare(request=request)
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
                    logger.printInfo("Exiting from WS loop")
                    break

                elif coin not in wsMethods:
                    raise error.RpcBadRequestError(
                        id=rpcPayload[ID],
                        message=f"Calling {coin} method when currency is not supported"
                    )

                elif rpcPayload[METHOD] not in wsMethods[coin]:
                    raise error.RpcBadRequestError(
                        id=rpcPayload[ID],
                        message=f"Calling unknown method aOperation for currency {coin}"
                    )

                else:
                    response = wsMethods[coin][rpcPayload[METHOD]](
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

    except httpError.Error as err:
        response = rpcutils.generateRPCResultResponse(
            payload[rpcutils.ID] if payload is not None else rpcutils.UNKNOWN_RPC_REQUEST_ID,
            err.jsonEncode()
        )

        logger.printError(f"Sending RPC http response to requester: {response}")

        await subscriber.sendMessage(response)

    finally:
        await subscriber.closeConnection(broker.Broker())
        logger.printInfo("Closing websocket")

    return subscriber.websocket
