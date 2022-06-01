#!/usr/bin/python
from aiohttp import web
import json
from logger import logger
from httputils.app import appModule
from httputils.router import Router
from httputils import httputils, error
from .constants import *
from . import adminutils

routes = web.RouteTableDef()


@routes.post(f"/{ADD_COIN_METHOD}")
async def addCoin(request):

    logger.printInfo("Executing addCoin method")

    if "x-api-key" not in request.headers or request.headers["x-api-key"] != adminutils.getApiKey():
        raise error.UnauthorizedError("Unauthorized")

    payload = httputils.parseJSONRequest(await request.read())

    requestSchema, responseSchema = adminutils.getAdminMethodSchemas(ADD_COIN_METHOD)

    err = httputils.validateJSONSchema(payload, requestSchema)
    if err is not None:
        raise error.BadRequestError(message=err.message)

    router = Router()
    response = router.addCoin(
        coin=payload["coin"],
        network=payload["network"],
        config=payload["config"]
    )

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.BadRequestError(message=err.message)

    return web.Response(
        text=json.dumps(response)
    )


@routes.post(f"/{REMOVE_COIN_METHOD}")
async def removeCoin(request):

    logger.printInfo("Executing removeCoin method")

    if "x-api-key" not in request.headers or request.headers["x-api-key"] != adminutils.getApiKey():
        raise error.UnauthorizedError("Unauthorized")

    payload = httputils.parseJSONRequest(await request.read())

    requestSchema, responseSchema = adminutils.getAdminMethodSchemas(REMOVE_COIN_METHOD)

    err = httputils.validateJSONSchema(payload, requestSchema)
    if err is not None:
        raise error.BadRequestError(message=err.message)

    router = Router()
    response = await router.removeCoin(
        coin=payload["coin"],
        network=payload["network"]
    )

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.BadRequestError(message=err.message)

    return web.Response(
        text=json.dumps(response)
    )


@routes.post(f"/{GET_COIN_METHOD}")
async def getCoin(request):

    logger.printInfo("Executing getCoin method")

    if "x-api-key" not in request.headers or request.headers["x-api-key"] != adminutils.getApiKey():
        raise error.UnauthorizedError("Unauthorized")

    payload = httputils.parseJSONRequest(await request.read())

    requestSchema, responseSchema = adminutils.getAdminMethodSchemas(GET_COIN_METHOD)

    err = httputils.validateJSONSchema(payload, requestSchema)
    if err is not None:
        raise error.BadRequestError(message=err.message)

    router = Router()
    response = router.getCoin(
        coin=payload["coin"],
        network=payload["network"]
    )

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.BadRequestError(message=err.message)

    return web.Response(
        text=json.dumps(response)
    )


@routes.post(f"/{UPDATE_COIN_METHOD}")
async def updateCoin(request):

    logger.printInfo("Executing getCoin method")

    if "x-api-key" not in request.headers or request.headers["x-api-key"] != adminutils.getApiKey():
        raise error.UnauthorizedError("Unauthorized")

    payload = httputils.parseJSONRequest(await request.read())

    requestSchema, responseSchema = adminutils.getAdminMethodSchemas(UPDATE_COIN_METHOD)

    err = httputils.validateJSONSchema(payload, requestSchema)
    if err is not None:
        raise error.BadRequestError(message=err.message)

    router = Router()
    response = await router.updateCoin(
        coin=payload["coin"],
        network=payload["network"],
        config=payload["config"]
    )

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.BadRequestError(message=err.message)

    return web.Response(
        text=json.dumps(response)
    )


adminModule = web.Application()
adminModule.add_routes(routes)


@appModule(moduleAppPath="/admin")
def getAdminModule():
    return adminModule
