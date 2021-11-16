#!/usr/bin/python3
import threading
from logger import logger
from .singleton import Singleton
from .subscribers import SubscriberInterface


class Broker(object, metaclass=Singleton):

    def __init__(self):

        self.topicSubscriptions = {}  # Topic -> [Sub1, Sub2]

    def attach(self, subscriber, topic=""):

        if not issubclass(type(subscriber), SubscriberInterface):
            logger.printWarning("Trying to attach unknown subscriber class")
            return

        if topic not in self.topicSubscriptions:
            self.topicSubscriptions[topic] = [subscriber]
        else:
            self.topicSubscriptions[topic].append(subscriber)

        logger.printInfo(f"Subscriber atached to topic [{topic}]")

    def detach(self, subscriber, topic=""):

        if not issubclass(type(subscriber), SubscriberInterface):
            logger.printWarning("Trying to detach unknown subscriber class")
            return

        if topic not in self.topicSubscriptions:
            logger.printWarning(f"Trying to detach subscriber from unknown topic [{topic}]")
        elif subscriber in self.topicSubscriptions[topic]:
            self.topicSubscriptions[topic].remove(subscriber)
            logger.printInfo(f"Subscriber detached from topic [{topic}]")
            if len(self.topicSubscriptions[topic]) == 0:
                logger.printWarning(f"No subscribers for topic [{topic}]")
                del self.topicSubscriptions[topic]
        else:
            logger.printInfo(f"Subscriber {subscriber.subscriberID} can not be detached because it is not subscribed to topic [{topic}]")

    def route(self, topic="", message=""):

        if topic in self.topicSubscriptions:

            for subscriber in self.topicSubscriptions[topic]:

                subscriberNotificationThread = threading.Thread(target=_notifySubscriber, args=(subscriber, topic, message))
                subscriberNotificationThread.start()

    def removeSubscriber(self, subscriber, topics):
        for topic in topics:
            self.detach(subscriber, topic)


def _notifySubscriber(subscriber, topic, message):
    subscriber.onMessage(topic, message)
