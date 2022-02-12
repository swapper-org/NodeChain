#!/usr/bin/python
import json
from aiohttp import web
from httputils.app import appModule
from logger import logger
from .constants import *
from utils import utils

routes = web.RouteTableDef()


@routes.get(f"/{GET_VERSION_METHOD}")
async def getVersion(request):

    logger.printInfo("Executing getVersion method")

    return web.Response(
        text=json.dumps(
            {
                "version": utils.getConfigProperty("version")
            }
        )
    )

infoModule = web.Application()
infoModule.add_routes(routes)


@appModule(moduleAppPath="/info")
def getAdminModule():
    return infoModule
