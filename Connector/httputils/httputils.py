#!/usr/bin/python3
import json
import random
import sys
from logger import logger
from webapp import WebApp
from aiohttp import web
from rpcutils import errorhandler, rpcutils


def postMethod(function):

    logger.printInfo(f"Registering new Post HTTP method {function.__name__}")

    async def wrapper(request):

        logger.printInfo(f"Executing HTTP method {function.__name__} over RPC")

        try:

            response = function(
                random.randint(1, sys.maxsize),
                parseHttpRequest(await request.read())
            )

            logger.printInfo(f"Sending response to requester: {response}")

            return web.Response(
                text=json.dumps(response),
                content_type=rpcutils.JSON_CONTENT_TYPE,
            )

        except errorhandler.Error as e:
            return web.Response(
                text=json.dumps(e.jsonEncode()),
                content_type=rpcutils.JSON_CONTENT_TYPE,
                status=e.code,
            )

    app = WebApp()
    app.add_routes([web.post(f"/{function.__name__}", wrapper)])

    return function


def getMethod(function):

    logger.printInfo(f"Registering new Get HTTP method {function.__name__}")

    async def wrapper(request):

        logger.printInfo(f"Executing HTTP method {function.__name__} over RPC")

        try:

            response = function(
                random.randint(1, sys.maxsize),
                {}
            )

            logger.printInfo(f"Sending response to requester: {response}")

            return web.Response(
                text=json.dumps(response),
                content_type=rpcutils.JSON_CONTENT_TYPE,
            )

        except errorhandler.Error as e:
            return web.Response(
                text=json.dumps(e.jsonEncode()),
                content_type=rpcutils.JSON_CONTENT_TYPE,
                status=e.code,
            )

    app = WebApp()
    app.add_routes([web.get(f"/{function.__name__}", wrapper)])

    return function


def parseHttpRequest(request):

    try:
        return json.loads(request)
    except Exception as e:
        logger.printError(f"Payload is not JSON message: {e}")
        raise errorhandler.BadRequestError(f"Payload is not JSON message: {e}")
