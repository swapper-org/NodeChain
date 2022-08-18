#!/usr/bin/python
from aiohttp import web
import json
from logger.logger import Logger
from .constants import *
from . import error


@web.middleware
async def jsonContentType(request, handler):

    response = await handler(request)

    response.headers["Content-Type"] = JSON_CONTENT_TYPE

    return web.Response(
        headers=response.headers,
        text=response.text,
        status=response.status
    )


@web.middleware
async def errorHandler(request, handler):

    try:
        return await handler(request)
    except error.Error as err:
        Logger.printError(f"Returning error in error handler {err.jsonEncode()}")
        return web.Response(
            status=err.code,
            text=json.dumps(err.jsonEncode())
        )
    except web.HTTPClientError as err:
        return web.Response(
            status=err.status,
            headers=err.headers,
            text=json.dumps(
                error.Error(message=err.text, code=err.status).jsonEncode()
            )
        )
    except Exception as err:
        Logger.printError("Returning unknown error in error handler")
        return web.Response(
            status=INTERNAL_SERVER_ERROR_CODE,
            text=json.dumps(
                error.InternalServerError(
                    message=str(err)
                ).jsonEncode()
            )
        )
