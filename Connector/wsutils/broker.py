#!/usr/bin/python3
import threading
from logger import logger
from .singleton import Singleton
from .subscribers import SubscriberInterface
from .constants import *
from .topics import TOPIC_SEPARATOR


class Broker(object, metaclass=Singleton):

    def __init__(self):

        self.topicSubscriptions = {}  # Topic -> [Sub1, Sub2]

    def attach(self, subscriber, topic=""):

        logger.printInfo(f"Attaching subscriber {subscriber.subscriberID} to topic [{topic}]")

        if not issubclass(type(subscriber), SubscriberInterface):
            logger.printWarning("Trying to attach unknown subscriber class")
            return {
                SUBSCRIBED: False
            }

        if topic not in self.topicSubscriptions:
            self.topicSubscriptions[topic] = []

        if subscriber not in self.topicSubscriptions[topic]:
            logger.printInfo(f"Subscriber {subscriber.subscriberID} atached successfully to topic [{topic}]")
            self.topicSubscriptions[topic].append(subscriber)
            return {
                SUBSCRIBED: True
            }
        else:
            logger.printInfo(f"Subscriber {subscriber.subscriberID} already atached to topic [{topic}]")
            return {
                SUBSCRIBED: False
            }

    def detach(self, subscriber, topic=""):

        logger.printInfo(f"Detaching subscriber {subscriber.subscriberID} from topic [{topic}]")

        if not issubclass(type(subscriber), SubscriberInterface):
            logger.printWarning("Trying to detach unknown subscriber class")
            return {
                UNSUBSCRIBED: False
            }

        if topic not in self.topicSubscriptions:
            logger.printWarning(f"Trying to detach subscriber {subscriber.subscriberID} from unknown topic [{topic}]")
            return {
                UNSUBSCRIBED: False
            }
        elif subscriber in self.topicSubscriptions[topic]:
            self.topicSubscriptions[topic].remove(subscriber)
            logger.printInfo(f"Subscriber {subscriber.subscriberID} detached from topic [{topic}]")

            if len(self.topicSubscriptions[topic]) == 0:
                logger.printWarning(f"No more subscribers for topic [{topic}]")
                del self.topicSubscriptions[topic]

            return {
                UNSUBSCRIBED: True
            }
        else:
            logger.printWarning(f"Subscriber {subscriber.subscriberID} can not be detached because it is not subscribed to topic [{topic}]")
            return {
                UNSUBSCRIBED: False
            }

    def route(self, topic="", message=""):

        logger.printInfo(f"Routing message of topic [{topic}]: {message}")

        if topic in self.topicSubscriptions:

            for subscriber in self.topicSubscriptions[topic]:

                subscriberNotificationThread = threading.Thread(target=_notifySubscriber, args=(subscriber, topic, message))
                subscriberNotificationThread.start()

    def removeSubscriber(self, subscriber):

        logger.printInfo(f"Removing subscriber {subscriber.subscriberID} from subsbribed topics")

        if not issubclass(type(subscriber), SubscriberInterface):
            logger.printWarning("Trying to remove unknown subscriber class")
            return

        for topic in subscriber.topicsSubscribed:
            self.detach(subscriber, topic)

    def isTopic(self, topic):
        return topic in self.topicSubscriptions

    def getSubTopics(self, topic):
        return [topicSubscription[len(topic) + 1:] for topicSubscription in self.topicSubscriptions if topic in topicSubscription]


def _notifySubscriber(subscriber, topic, message):
    subscriber.onMessage(topic, message)
