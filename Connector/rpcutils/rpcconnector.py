#!/usr/bin/python
import aiohttp
from logger import logger
from . import error
from .constants import *
import asyncio


class RPCConnector():

    @staticmethod
    async def request(endpoint, id, method, params):

        try:

            payload = {
                ID: id,
                METHOD: method,
                PARAMS: params,
                JSON_RPC: JSON_RPC_VERSION
            }

            logger.printInfo(f"Making RPC Request to {endpoint}. Payload: {payload}")

            await asyncio.sleep(5)

            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint, json=payload) as resp:
                    if resp.status != 200:
                        raise error.RpcBadGatewayError(id=id, message="Bad Gateway")
                    try:
                        response = await resp.json()
                    except Exception as e:
                        logger.printError(f"Json in client response is not supported: {str(e)}")
                        raise error.RpcInternalServerError(
                            id=id,
                            message=f"Json in client response is not supported: {str(e)}"
                        )
        except Exception as e:
            logger.printError(f"Request to client could not be completed: {str(e)}")
            raise error.RpcBadRequestError(
                id=id,
                message=f"Request to client could not be completed: {str(e)}"
            )

        logger.printInfo(f"Response received from {endpoint}: {response}")

        if ERROR in response and response[ERROR] is not None:
            logger.printError(f"Exception occured in server: {response[ERROR]}")
            raise error.RpcBadRequestError(
                id=id,
                message=f"Exception occured in server: {response[ERROR]}"
            )

        return response[RESULT]
