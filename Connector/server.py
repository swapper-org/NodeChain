#!/usr/bin/python3
from aiohttp import web
import aiohttp_cors
import importlib
from httputils import middleware
from httputils.router import Router
from httputils.app import App, appModules
from httputils.constants import JSON_CONTENT_TYPE
from rpcutils import middleware as rpcMiddleware
from wsutils import broker
from logger.logger import Logger
from utils import utils


async def onPrepare(request, response):

    response.headers["Content-Type"] = JSON_CONTENT_TYPE


async def onShutdown(app):

    Logger.printInfo("Application is shutting down")

    for subscriberID, sub in list(broker.Broker().subs.items()):
        await sub.close(broker.Broker())


async def onStartup(app):

    backUpConfigs = utils.getBackupConfigs()

    for coin, networks in backUpConfigs.items():
        for networkName, netwrokConfig in networks.items():
            logger.printInfo(f"Loading backup config for {coin} for {networkName}.")
            await Router().addCoin(coin=coin, network=networkName, config=netwrokConfig)


def runServer():

    mainApp = App(middlewares=[
        middleware.errorHandler,
        rpcMiddleware.errorHandler
    ])

    mainApp.on_response_prepare.append(onPrepare)
    mainApp.on_shutdown.append(onShutdown)
    mainApp.on_startup.append(onStartup)

    modules = [
        "admin",
        "info"
    ]

    Logger.printInfo("Registering app modules")

    availableCurrencies = utils.getAvailableCurrencies()

    for module in (modules + availableCurrencies):
        importlib.__import__(module)

    for appModule in appModules:
        mainApp.add_subapp(appModule, appModules[appModule])

    router = Router()
    mainApp.add_routes(
        [
            web.post("/{coin}/{network}/rpc", router.doRPCRoute),
            web.post("/{coin}/{network}/{standard}/rpc", router.doRPCRoute),
            web.get("/{coin}/{network}/ws", router.doWsRoute),
            web.post("/{coin}/{network}/callback/{callbackName}", router.handleCallback),
            web.post("/{coin}/{network}/{method}", router.doHTTPRoute),
            web.get("/{coin}/{network}/{method}", router.doHTTPRoute),
            web.post("/{coin}/{network}/{standard}/{method}", router.doHTTPRoute),
            web.get("/{coin}/{network}/{standard}/{method}", router.doHTTPRoute)
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

    Logger.printInfo("Starting connector")

    web.run_app(mainApp, port=80)


if __name__ == '__main__':
    runServer()
