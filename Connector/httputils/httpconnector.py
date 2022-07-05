#!/usr/bin/python
from logger import logger
from . import error
from http import HTTPStatus
import aiohttp


class HTTPConnector:

    @staticmethod
    async def get(endpoint, path="", params=None, headers=None):

        logger.printInfo(f"Making HTTP Get request to {endpoint}. Params: {params}")

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{endpoint}{path}", headers=headers, params=params) as resp:
                if resp.status != HTTPStatus.OK:
                    raise error.BadGatewayError("Bad Gateway")
                try:
                    response = await resp.json()
                except aiohttp.ContentTypeError as err:
                    logger.printError(f"Json in client response is not supported: {str(err)}")
                    raise error.BadGatewayError("Bad Gateway")

        logger.printInfo(f"Response received from {endpoint}: {response}")

        return response

    @staticmethod
    async def post(endpoint, path="", data=None):

        logger.printInfo(f"Making HTTP Post request to {endpoint}.")

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{endpoint}{path}", json=data) as resp:
                if resp.status != HTTPStatus.OK:
                    raise error.BadGatewayError(message="Bad Gateway")
                try:
                    response = await resp.json()
                except aiohttp.ContentTypeError as err:
                    logger.printError(f"Json in client response is not supported: {str(err)}")
                    raise error.BadGatewayError("Bad Gateway")

        logger.printInfo(f"Response received from {endpoint}: {response}")

        return response
