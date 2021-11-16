import abc
from aiohttp import web
import uuid
from logger import logger
import time
from random import randint


class SubscriberInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            (hasattr(subclass, "subscribeToTopic") and callable(subclass.subscribeToTopic)) and
            (hasattr(subclass, "unsubscribeFromTopic") and callable(subclass.unsubscribeFromTopic)) and
            (hasattr(subclass, "onMessage") and callable(subclass.onMessage)) and
            (hasattr(subclass, "onClose") and callable(subclass.onMessage))
        )


class Subscriber():

    def __init__(self):
        self.subscriberID = uuid.uuid4()
        self._topicsSubscribed = []
        self.websocket = web.WebSocketResponse(heartbeat=60)

    @property
    def topicsSubscribed(self):
        return self._topicsSubscribed

    def subscribeToTopic(self, broker, topic):
        if topic not in self._topicsSubscribed:
            broker.attach(self, topic)

    def unsubscribeFromTopic(self, broker, topic):
        if topic in self._topicsSubscribed:
            broker.detach(self, topic)

    def onClose(self, broker):
        broker.removeSubscriber(self)


class WSSubscriber(Subscriber):

    def onMessage(self, topic, message):
        time.sleep(randint(1, 3))
        logger.printInfo(f"New message for WS Subscriber {self.subscriberID} for topic [{topic}]: {message}")
        return message, topic


class TestSubscriber(Subscriber):

    def onMessage(self, topic, message):
        time.sleep(randint(1, 3))
        logger.printInfo(f"New message for Test Subscriber {self.subscriberID} for topic [{topic}]: {message}")
        return message, topic
