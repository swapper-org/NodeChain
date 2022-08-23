#!/usr/bin/python
import aiohttp
from logger.logger import Logger
from . import error
from .constants import *
from http import HTTPStatus


class RPCConnector:

    @staticmethod
    async def request(endpoint, id, method, params):

        payload = {
            ID: id,
            METHOD: method,
            PARAMS: params,
            JSON_RPC: JSON_RPC_VERSION
        }

        Logger.printDebug(f"Making RPC Request to {endpoint}. Payload: {payload}")

        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, json=payload) as resp:

                if resp.status != HTTPStatus.OK:
                    raise error.RpcBadGatewayError(id=id)
                try:
                    response = await resp.json()
                except aiohttp.ContentTypeError as err:
                    Logger.printError(f"Json in client response is not supported: {str(err)}")
                    raise error.RpcBadGatewayError(id=id)

        Logger.printDebug(f"Response received from {endpoint}: {response}")

        if ERROR in response and response[ERROR] is not None:
            Logger.printError(f"Exception occurred in server: {response[ERROR]}")
            raise error.RpcBadGatewayError(id=id)

        return response[RESULT]
