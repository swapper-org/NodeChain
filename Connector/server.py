#!/usr/bin/python3
from aiohttp import web
import aiohttp_cors
import importlib
from httputils import middleware
from httputils.router import Router
from httputils.app import App, appModules
from httputils.constants import JSON_CONTENT_TYPE
from rpcutils import middleware as rpcMiddleware
from logger import logger
# from utils import utils


async def onPrepare(request, response):

    response.headers["Content-Type"] = JSON_CONTENT_TYPE

# TODO: Create onShutdown handler to close everything


def runServer():

    mainApp = App(middlewares=[
        middleware.errorHandler,
        rpcMiddleware.errorHandler
    ])

    mainApp.on_response_prepare.append(onPrepare)

    modules = [
        "admin"
    ]

    logger.printInfo("Registering app modules")

    # availableCurrencies = utils.getAvailableCurrencies()

    availableCurrencies = ["eth", "btc", "xmr"]

    for module in (modules + availableCurrencies):
        importlib.__import__(module)

    logger.printInfo("Loading app modules")

    for appModule in appModules:
        mainApp.add_subapp(appModule, appModules[appModule])

    router = Router()
    mainApp.add_routes(
        [
            web.post("/{coin}/{network}/{method}", router.doRoute),
            web.get("/{coin}/{network}/ws", router.doWsRoute),
            web.post("/{coin}/{network}/callback/{callbackName}", router.handleCallback)
        ]
    )
    cors = aiohttp_cors.setup(mainApp, defaults={
        "*": aiohttp_cors.ResourceOptions(
            expose_headers="*",
            allow_headers="*",
        )
    })

    for route in list(mainApp.router.routes()):
        cors.add(route)

    logger.printInfo("Starting connector")

    # TODO: Do not hardcode port
    web.run_app(mainApp, port=80)


if __name__ == '__main__':
    runServer()
