from aiohttp import web

class ServerWebSocket:

    def __init__(self):
        super().__init__()
        self._subscriptions = []
        self.websocket = web.WebSocketResponse(heartbeat=60)

    def addAddress(self, address):
        self._subscriptions.append(address)

    def removeAddress(self, address):
        self._subscriptions.remove(address)

    def clean(self):
        self._subscriptions.clear()

    @property
    def subscriptions(self):
        return self._subscriptions