#!/usr/bin/python3
from .constants import *
from wsutils import wsutils
from wsutils.broker import Broker
from wsutils import topics
from wsutils.subscriptionshandler import SubcriptionsHandler
from rpcutils import rpcutils, errorhandler as rpcerrorhandler
from . import utils
from logger import logger


@wsutils.webSocketMethod
def subscribeAddressBalance(subscriber, id, params):

    logger.printInfo(f"Executing WS method subscribeAddressBalance with id {id} and params {params}")

    requestSchema = utils.getWSRequestMethodSchema(SUBSCRIBE_ADDRESS_BALANCE)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return subscriber.subscribeToTopic(Broker(), topics.ADDRESS_BALANCE_TOPIC + topics.TOPIC_SEPARATOR + params[ADDRESS])


@wsutils.webSocketMethod
def unsubscribeAddressBalance(subscriber, id, params):

    logger.printInfo(f"Executing WS method unsubscribeAddressBalance with id {id} and params {params}")

    requestSchema = utils.getWSRequestMethodSchema(UNSUBSCRIBE_ADDRESS_BALANCE)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return subscriber.unsubscribeFromTopic(Broker(), topics.ADDRESS_BALANCE_TOPIC + topics.TOPIC_SEPARATOR + params[ADDRESS])
