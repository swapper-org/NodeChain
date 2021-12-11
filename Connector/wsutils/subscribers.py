#!/usr/bin/python3
import abc
import asyncio
from aiohttp import web, WSCloseCode
import json
import uuid
from logger import logger


class SubscriberInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            (hasattr(subclass, "subscribeToTopic") and callable(subclass.subscribeToTopic)) and
            (hasattr(subclass, "unsubscribeFromTopic") and callable(subclass.unsubscribeFromTopic)) and
            (hasattr(subclass, "onMessage") and callable(subclass.onMessage)) and
            (hasattr(subclass, "closeConnection") and callable(subclass.onMessage))
        )


class Subscriber:

    def __init__(self):
        self.subscriberID = uuid.uuid4()
        self._topicsSubscribed = []

    @property
    def topicsSubscribed(self):
        return self._topicsSubscribed

    def subscribeToTopic(self, broker, topic):
        self._topicsSubscribed.append(topic.name)
        return broker.attach(self, topic)

    def unsubscribeFromTopic(self, broker, topicName):
        self._topicsSubscribed.remove(topicName)
        return broker.detach(self, topicName)

    def closeConnection(self, broker):
        broker.removeSubscriber(self)


class WSSubscriber(Subscriber):

    def __init__(self):
        super().__init__()
        self.websocket = web.WebSocketResponse(heartbeat=60)

    def onMessage(self, topicName, message):
        logger.printInfo(f"New message for WS Subscriber {self.subscriberID} for topic [{topicName}]: {message}")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(notify(self.websocket, message))
        return message, topicName

    async def closeConnection(self, broker):
        super().closeConnection(broker)
        await self.websocket.close(code=WSCloseCode.GOING_AWAY, message="Server shutdown".encode())

    async def sendMessage(self, message):
        await self.websocket.send_str(
            json.dumps(
                message
            )
        )


async def notify(ws, message):
    await ws.send_str(
        json.dumps(
            message
        )
    )


class DummySubscriber(Subscriber):

    def onMessage(self, topicName, message):
        logger.printInfo(f"New message for Dummy Subscriber {self.subscriberID} for topic [{topicName}]: {message}")
        return message, topicName


class ListenerSubscriber(Subscriber):

    def __init__(self):
        super().__init__()
        self.messageReceived = False

    def onMessage(self, topicName, message):
        logger.printInfo(f"New message for Listener Subscriber {self.subscriberID} for topic [{topicName}]: {message}")
        self.messageReceived = True
