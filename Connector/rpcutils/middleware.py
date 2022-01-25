#!/usr/bin/python
from aiohttp import web
import json
from logger import logger
from . import error


@web.middleware
async def errorHandler(request, handler):

    try:
        return await handler(request)
    except error.RpcError as err:
        logger.printError(f"Returning RPC error in error handler {err.jsonEncode()}")
        return web.Response(
            status=err.code,
            text=json.dumps(err.jsonEncode())
        )
