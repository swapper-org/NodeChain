#!/usr/bin/python
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


def callMethod(coin, config, request):

    payload = rpcutils.parseJsonRpcRequest(request)
    if coin not in rpcMethods:
        raise error.RpcBadRequestError(
            id=payload[ID],
            message=f"Calling {coin} method when currency is not supported"
        )
    if payload[METHOD] not in rpcMethods[coin]:
        raise error.RpcBadRequestError(
            id=payload[ID],
            message=f"Calling unknown method aOperation for currency {coin}"
        )

    return rpcMethods[coin][payload[METHOD]](payload, config)
