#!/usr/bin/python
import aiohttp
from logger import logger
from . import error
from .constants import *
import asyncio


class RPCConnector():

    @staticmethod
    async def request(endpoint, id, method, params):

        payload = {
            ID: id,
            METHOD: method,
            PARAMS: params,
            JSON_RPC: JSON_RPC_VERSION
        }

        logger.printInfo(f"Making RPC Request to {endpoint}. Payload: {payload}")

        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, json=payload) as resp:
                if resp.status != 200:
                    raise error.RpcBadGatewayError(id=id, message="Bad Gateway")
                try:
                    response = await resp.json()
                except aiohttp.ContentTypeError as err:
                    logger.printError(f"Json in client response is not supported: {str(err)}")
                    raise error.BadGatewayError("Bad Gateway")

        logger.printInfo(f"Response received from {endpoint}: {response}")

        if ERROR in response and response[ERROR] is not None:
            logger.printError(f"Exception occured in server: {response[ERROR]}")
            raise error.RpcBadGatewayError(
                id=id,
                message=f"Exception occured in server: {response[ERROR]}"
            )

        return response[RESULT]
