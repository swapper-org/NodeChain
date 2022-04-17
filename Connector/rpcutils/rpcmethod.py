#!/usr/bin/python
from httputils import httputils
from logger import logger
from . import rpcutils
from .constants import *
from . import error


rpcMethods = {}


def rpcMethod(coin, standard=None):

    wrapperApiId = coin if standard is None else f"{coin}/{standard}"

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

        if wrapperApiId not in rpcMethods:
            logger.printInfo(f"Registering new JSON RPC method {function.__name__} for wrapper API {wrapperApiId}")
            rpcMethods[wrapperApiId] = {function.__name__: wrapper}

        elif function.__name__ not in rpcMethods[wrapperApiId]:
            logger.printInfo(f"Registering new JSON RPC method {function.__name__} for wrapper API {wrapperApiId}")
            rpcMethods[wrapperApiId][function.__name__] = wrapper

        else:
            logger.printError(f"JSON RPC Method {function.__name__} already registered for wrapper API {wrapperApiId}")

        return function

    return _rpcMethod


async def callMethod(coin, config, request, standard=None):

    payload = httputils.parseJSONRequest(await request.read())
    rpcPayload = rpcutils.parseJsonRpcRequest(payload)
    wrapperApiId = coin if standard is None else f"{coin}/{standard}"

    if wrapperApiId not in rpcMethods:
        raise error.RpcBadRequestError(
            id=rpcPayload[ID],
            message=f"Calling {wrapperApiId} method when wrapper API is not supported"
        )
    if rpcPayload[METHOD] not in rpcMethods[wrapperApiId]:
        raise error.RpcNotFoundError(
            id=rpcPayload[ID],
            message=f"Calling unknown method for wrapper API {wrapperApiId}"
        )

    return rpcMethods[wrapperApiId][payload[METHOD]](rpcPayload, config)
