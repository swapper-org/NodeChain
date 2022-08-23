#!/usr/bin/python
import json
from aiohttp import web
from httputils.app import appModule
from logger.logger import Logger
from .constants import *
from utils import utils

routes = web.RouteTableDef()


@routes.get(f"/{GET_VERSION_METHOD}")
async def getVersion(request):

    Logger.printDebug("Executing getVersion method")

    return web.Response(
        text=json.dumps(
            {
                "version": utils.getConfigProperty("version")
            }
        )
    )


@routes.get(f"/{GET_STATUS}")
async def getStatus(request):

    Logger.printDebug("Executing getStatus method")

    return web.Response(
        text=json.dumps(
            {
                "status": "Connector is running"
            }
        )
    )

infoModule = web.Application()
infoModule.add_routes(routes)


@appModule(moduleAppPath="/info")
def getAdminModule():
    return infoModule
