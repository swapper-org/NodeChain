#!/usr/bin/python3
import re
import threading
from logger import logger
from patterns import Singleton
from .subscribers import SubscriberInterface
from .constants import *


class Broker(object, metaclass=Singleton.Singleton):

    def __init__(self):

        self.topicSubscriptions = {}  # Topic -> {"Subs":[Sub1, Sub2], "ClosingFunc":func}
        self.subs = {}

    def register(self, subscriber):
        logger.printInfo(f"New subscriber with id [{subscriber.subscriberID}] registered")
        self.subs[subscriber.subscriberID] = subscriber

    def unregister(self, subscriber):
        logger.printInfo(f"Subscriber with id [{subscriber.subscriberID}] unregistered")
        del self.subs[subscriber.subscriberID]

    def attach(self, subscriber, topic):

        logger.printInfo(f"Attaching subscriber {subscriber.subscriberID} to topic [{topic.name}]")

        if not issubclass(type(subscriber), SubscriberInterface):
            logger.printWarning("Trying to attach unknown subscriber class")
            return {
                SUBSCRIBED: False
            }

        if topic.name not in self.topicSubscriptions:
            self.topicSubscriptions[topic.name] = {
                SUBSCRIBERS: [],
                CLOSING_TOPIC_FUNC: topic.closingHandler
            }

        if subscriber not in self.topicSubscriptions[topic.name][SUBSCRIBERS]:
            logger.printInfo(f"Subscriber {subscriber.subscriberID} attached successfully to topic [{topic.name}]")
            self.topicSubscriptions[topic.name][SUBSCRIBERS].append(subscriber)
            return {
                SUBSCRIBED: True
            }
        else:
            logger.printInfo(f"Subscriber {subscriber.subscriberID} already attached to topic [{topic.name}]")
            return {
                SUBSCRIBED: False
            }

    def detach(self, subscriber, topicName=""):

        logger.printInfo(f"Detaching subscriber {subscriber.subscriberID} from topic [{topicName}]")

        if not issubclass(type(subscriber), SubscriberInterface):
            logger.printWarning("Trying to detach unknown subscriber class")
            return {
                UNSUBSCRIBED: False
            }

        if topicName not in self.topicSubscriptions:
            logger.printWarning(
                f"Trying to detach subscriber {subscriber.subscriberID} from unknown topic [{topicName}]"
            )
            return {
                UNSUBSCRIBED: False
            }
        elif subscriber in self.topicSubscriptions[topicName][SUBSCRIBERS]:
            self.topicSubscriptions[topicName][SUBSCRIBERS].remove(subscriber)
            logger.printInfo(f"Subscriber {subscriber.subscriberID} detached from topic [{topicName}]")

            if not self.topicHasSubscribers(topicName=topicName):

                logger.printWarning(f"No more subscribers for topic [{topicName}]")
                topicClosingFunc = self.topicSubscriptions[topicName][CLOSING_TOPIC_FUNC]
                logger.printInfo(f"Calling closing func to topic [{topicName}]")
                if topicClosingFunc is not None:
                    topicClosingFunc(topicName)

                del self.topicSubscriptions[topicName]

            return {
                UNSUBSCRIBED: True
            }
        else:
            logger.printWarning(
                f"Subscriber {subscriber.subscriberID} can not be detached because"
                f" it is not subscribed to topic [{topicName}]")
            return {
                UNSUBSCRIBED: False
            }

    def route(self, topicName="", message=""):

        logger.printInfo(f"Routing message of topic [{topicName}]: {message}")

        if topicName in self.topicSubscriptions:

            for subscriber in self.topicSubscriptions[topicName][SUBSCRIBERS]:

                threading.Thread(
                    target=_notifySubscriber,
                    args=(subscriber, topicName, message),
                    daemon=True
                ).start()

    def removeSubscriber(self, subscriber):

        logger.printInfo(f"Removing subscriber {subscriber.subscriberID} from subsbribed topics")

        if not issubclass(type(subscriber), SubscriberInterface):
            logger.printWarning("Trying to remove unknown subscriber class")
            return False

        for topicName in subscriber.topicsSubscribed:
            self.detach(subscriber, topicName)

        return True

    def isTopic(self, topicName):
        return topicName in self.topicSubscriptions

    def getSubTopics(self, topicName):

        subTopics = []

        for topic in self.topicSubscriptions:
            matches = re.finditer(f"{topicName}([a-z0-9A-Z/]+)", topic, re.MULTILINE)
            found = False
            for match in matches:
                for group in match.groups():
                    subTopics.append(group[1:])
                    found = True
                    break
                if found:
                    break

        return subTopics

    def topicHasSubscribers(self, topicName):
        if topicName in self.topicSubscriptions:
            return len(self.topicSubscriptions[topicName][SUBSCRIBERS]) != 0
        return False

    def getTopicSubscribers(self, topicName):

        if topicName in self.topicSubscriptions:
            return self.topicSubscriptions[topicName][SUBSCRIBERS]
        return []

    def getTopicNameSubscriptions(self):
        return list(self.topicSubscriptions.keys())


def _notifySubscriber(subscriber, topicName, message):
    subscriber.onMessage(topicName, message)
