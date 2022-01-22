#!/usr/bin/python3
from aiohttp import web
import aiohttp_cors
import importlib
from logger import logger
from httputils import middleware
from httputils.app import App, appModules


def runServer():

    mainApp = App(middlewares=[
        middleware.jsonContentType,
        middleware.errorHandler
    ])

    modules = [
        "admin"
    ]

    logger.printInfo("Registering app modules")
    for module in modules:
        importlib.__import__(module)

    logger.printInfo("Loading app modules")

    for appModule in appModules:
        mainApp.add_subapp(appModule, appModules[appModule])

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
