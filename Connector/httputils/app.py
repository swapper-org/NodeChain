#!/usr/bin/python
from aiohttp import web
from logger.logger import Logger

appModules = {}


class App(web.Application):

    def __init__(self, middlewares=()):
        super().__init__(middlewares=middlewares)
        self.clientSessions = []
        self.zmqConnections = []

    def addWSClientSession(self, clientSession):
        if clientSession not in self.clientSessions:
            self.clientSessions.append(clientSession)

    async def closeWSClientSession(self, clientSession):
        if clientSession in self.clientSessions:
            await clientSession.close()
            self.clientSessions.remove(clientSession)

    async def closeAllWSClientSessions(self):
        for clientSession in list(self.clientSessions):
            await self.closeWSClientSession(clientSession)

    def addZMQSocket(self, zmqConnection):
        if zmqConnection not in self.zmqConnections:
            self.clientSessions.append(zmqConnection)

    async def closeZMQSocket(self, zmqConnection):
        if zmqConnection in self.clientSessions:
            await zmqConnection.close()
            self.clientSessions.remove(zmqConnection)

    async def closeAllZMQSocket(self):
        for zmqConnection in list(self.zmqConnections):
            await self.closeWSClientSession(zmqConnection)


def appModule(moduleAppPath):

    def moduleWrapper(function):

        if moduleAppPath in appModules:
            Logger.printWarning(f"Module {moduleAppPath} already registered")
        else:
            Logger.printDebug(f"Registering {moduleAppPath} module")
            appModules[moduleAppPath] = function()

    return moduleWrapper
