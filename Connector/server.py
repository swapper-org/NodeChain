#!/usr/bin/python3
from aiohttp import web
import aiohttp_cors
import importlib
from httputils import middleware
from httputils.router import Router
from httputils.app import App, appModules
from rpcutils import middleware as rpcMiddleware
from logger import logger
from utils import utils


def runServer():

    mainApp = App(middlewares=[
        middleware.jsonContentType,
        middleware.errorHandler,
        rpcMiddleware.errorHandler
    ])

    modules = [
        "admin"
    ]

    logger.printInfo("Registering app modules")

    # availableCurrencies = utils.getAvailableCurrencies()

    availableCurrencies = ["eth"]
    for module in (modules + availableCurrencies):
        importlib.__import__(module)

    logger.printInfo("Loading app modules")

    for appModule in appModules:
        mainApp.add_subapp(appModule, appModules[appModule])

    router = Router()
    mainApp.add_routes(
        [
            web.post("/{coin}/{network}/{method}", router.doRoute)
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

    web.run_app(mainApp, port=80)


if __name__ == '__main__':
    runServer()
