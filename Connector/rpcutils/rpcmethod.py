#!/usr/bin/python
from httputils import httputils
from logger import logger
from . import rpcutils
from .constants import *
from . import error


rpcMethods = {}


def rpcMethod(coin):

    def _rpcMethod(function):

        def wrapper(request, config):

            response = function(
                request[ID],
                request[PARAMS],
                config
            )
            return {
                ID: request[ID],
                JSON_RPC: JSON_RPC_VERSION,
                RESULT: response
            }

        if coin not in rpcMethods:
            logger.printInfo(f"Registering new JSON RPC method {function.__name__} for currency {coin}")
            rpcMethods[coin] = {function.__name__: wrapper}

        elif function.__name__ not in rpcMethods[coin]:
            logger.printInfo(f"Registering new JSON RPC method {function.__name__} for currency {coin}")
            rpcMethods[coin][function.__name__] = wrapper

        else:
            logger.printError(f"JSON RPC Method {function.__name__} already registered for currency {coin}")

        return function

    return _rpcMethod


async def callMethod(coin, config, request):

    payload = httputils.parseJSONRequest(await request.read())
    rpcPayload = rpcutils.parseJsonRpcRequest(payload)

    if coin not in rpcMethods:
        raise error.RpcBadRequestError(
            id=rpcPayload[ID],
            message=f"Calling {coin} method when currency is not supported"
        )
    if rpcPayload[METHOD] not in rpcMethods[coin]:
        raise error.RpcBadRequestError(
            id=rpcPayload[ID],
            message=f"Calling unknown method {rpcPayload[METHOD]} for currency {coin}"
        )

    return rpcMethods[coin][payload[METHOD]](rpcPayload, config)
