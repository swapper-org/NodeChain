#!/usr/bin/python3
from logger import logger

webSockets = []
webSocketMethods = {}
webSocketClosingHandlers = []


def webSocket(f):
    logger.printInfo(f"Registering new websocket: {f.__name__}")
    webSockets.append(f)
    return f


def webSocketMethod(f):
    logger.printInfo(f"Registering new websocket method: {f.__name__}")
    webSocketMethods[f.__name__] = f
    return f


def webSocketClosingHandler(f):
    logger.printInfo(f"Registering new websocket handler: {f.__name__}")
    webSocketClosingHandlers.append(f)
