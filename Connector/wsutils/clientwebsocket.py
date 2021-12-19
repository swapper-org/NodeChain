#!/usr/bin/python3
from aiohttp import ClientSession


class ClientWebSocket(ClientSession):

    def __init__(self, url):
        super().__init__()
        self.websocket = None
        self.url = url

    async def connect(self):
        """Connect to the WebSocket."""
        self.websocket = await self.ws_connect(self.url)

    async def close(self):
        """Close the WebSocket."""
        await super().close()

    async def send(self, message):
        """Send a message to the WebSocket."""
        assert self.websocket is not None, "You must connect first!"
        await self.websocket.send_json(message)
        print("Sent:", message)

    async def receive(self):
        """Receive one message from the WebSocket."""
        assert self.websocket is not None, "You must connect first!"
        return (await self.websocket.receive()).data

    async def read(self):
        """Read messages from the WebSocket. DEBUG purposes"""
        assert self.websocket is not None, "You must connect first!"

        while await self.websocket.receive():
            message = await self.receive()
            print("Received:", message)
            if message == "Echo 9!":
                break
