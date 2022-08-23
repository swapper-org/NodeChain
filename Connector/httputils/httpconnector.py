#!/usr/bin/python
from logger.logger import Logger
from . import error
from http import HTTPStatus
import aiohttp


class HTTPConnector:

    @staticmethod
    async def get(endpoint, path="", params=None, headers=None):

        Logger.printDebug(f"Making HTTP Get request to {endpoint}. Params: {params}")

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{endpoint}{path}", headers=headers, params=params) as resp:

                if resp.status != HTTPStatus.OK:
                    raise error.BadGatewayError()

                try:
                    response = await resp.json()
                except aiohttp.ContentTypeError as err:
                    Logger.printError(f"Json in client response is not supported: {str(err)}")
                    raise error.BadGatewayError()

        Logger.printDebug(f"Response received from {endpoint}: {response}")

        return response

    @staticmethod
    async def post(endpoint, path="", data=None):

        Logger.printDebug(f"Making HTTP Post request to {endpoint}.")

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{endpoint}{path}", json=data) as resp:

                if resp.status != HTTPStatus.OK:
                    raise error.BadGatewayError()
                try:
                    response = await resp.json()
                except aiohttp.ContentTypeError as err:
                    Logger.printError(f"Json in client response is not supported: {str(err)}")
                    raise error.BadGatewayError()

        Logger.printDebug(f"Response received from {endpoint}: {response}")

        return response
