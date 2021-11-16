import abc
from logger import logger


class PublisherInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "publish") and callable(subclass.publish)
        )


class Publisher():

    def publish(self, broker, topic, message):
        logger.printInfo(f"Publishing new message for topic [{topic}]: {message}")
        broker.route(topic, message)
