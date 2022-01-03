from aiohttp import web


class WebApp():

    instance = None

    def __new__(cls):

        if not WebApp.instance:
            WebApp.instance = App()

        return WebApp.instance


class App(web.Application):

    def __init__(self):
        super().__init__()
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
