#!/usr/bin/python3
from logger import logger
from wsutils import wsutils, topics
from wsutils.broker import Broker
from rpcutils import rpcutils, errorhandler as rpcerrorhandler
from . import apirpc, utils
from .constants import *
from .connector import BITCOIN_CALLBACK_ENDPOINT


@wsutils.webSocketMethod
def subscribeAddressBalance(subscriber, id, params):

    logger.printInfo(f"Executing WS method subscribeAddressBalance with id {id} and params {params}")

    requestSchema = utils.getWSRequestMethodSchema(SUBSCRIBE_ADDRESS_BALANCE)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    broker = Broker()
    addrBalanceTopic = topics.ADDRESS_BALANCE_TOPIC + topics.TOPIC_SEPARATOR + params[ADDRESS]
    topic = topics.Topic(addrBalanceTopic, utils.closeAddrBalanceTopic)

    if not broker.isTopic(addrBalanceTopic):

        response = apirpc.notify(
            id,
            {
                ADDRESS: params[ADDRESS],
                CALLBACK_ENDPOINT: BITCOIN_CALLBACK_ENDPOINT
            }
        )

        if not response[SUCCESS]:
            logger.printError(f"Can not subscribe {params[ADDRESS]} to node")
            raise rpcerrorhandler.BadRequestError(f"Can not subscribe {params[ADDRESS]} to node")

    return subscriber.subscribeToTopic(broker, topic)


@wsutils.webSocketMethod
def unsubscribeAddressBalance(subscriber, id, params):

    logger.printInfo(f"Executing WS method unsubscribeAddressBalance with id {id} and params {params}")

    requestSchema = utils.getWSRequestMethodSchema(UNSUBSCRIBE_ADDRESS_BALANCE)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    broker = Broker()
    addrBalanceTopic = topics.ADDRESS_BALANCE_TOPIC + topics.TOPIC_SEPARATOR + params[ADDRESS]

    unsubscribeResponse = subscriber.unsubscribeFromTopic(broker, addrBalanceTopic)

    if not broker.isTopic(addrBalanceTopic):

        response = apirpc.notify(
            id,
            {
                ADDRESS: params[ADDRESS],
                CALLBACK_ENDPOINT: ""
            }
        )

        if not response[SUCCESS]:
            logger.printError(f"Can not unsubscribe {params[ADDRESS]} to node")
            raise rpcerrorhandler.BadRequestError(f"Can not unsubscribe {params[ADDRESS]} to node")

    return unsubscribeResponse
