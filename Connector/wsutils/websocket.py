#!/usr/bin/python
from logger import logger

# TODO: Create sync lock over webSockets
webSockets = {}  # {coin-> network -> []}


class WebSocket:

    def __init__(self, websocket):
        self._webSocket = websocket

    def __call__(self, coin, config):

        def start():
            pass

        def stop():
            pass

        self._webSocket.start = start \
            if not hasattr(self._webSocket, "start") or not callable(self._webSocket.start) \
            else self._webSocket.start

        self._webSocket.stop = stop \
            if not hasattr(self._webSocket, "stop") or not callable(self._webSocket.stop) \
            else self._webSocket.stop

        ws = self._webSocket(coin, config)

        if coin not in webSockets:
            webSockets[coin] = {
                config.networkName: []
            }
        elif coin in webSockets and config.networkName not in webSockets[coin]:
            webSockets[coin][config.networkName] = []

        logger.printInfo(f"Registering new WebSocket for {config.networkName} network for {coin} currency")
        webSockets[coin][config.networkName].append(ws)

        return ws


async def startWebSockets(coin, networkName):

    if coin not in webSockets:
        logger.printInfo(f"There are no websockets for {coin} currency")
        return

    if networkName not in webSockets[coin]:
        logger.printInfo(f"There are no websockets for {networkName} network for{coin} currency")
        return

    for webSocket in webSockets[coin][networkName]:
        await webSocket.start()


async def stopWebSockets(coin, networkName):

    if coin not in webSockets:
        logger.printInfo(f"There are no websockets for {coin} currency")
        return False

    if networkName not in webSockets[coin]:
        logger.printInfo(f"There are no websockets for {networkName} network for{coin} currency")
        return False

    for webSocket in webSockets[coin][networkName]:
        await webSocket.stop()

    logger.printInfo(f"Websockets stopped for {networkName} network for {coin} currency")
    del webSockets[coin][networkName]
    if len(webSockets[coin]) == 0:
        del webSockets[coin]

    return True
