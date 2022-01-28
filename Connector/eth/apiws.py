#!/usr/bin/python3
from logger import logger
from httputils import httputils
from rpcutils import error
from wsutils import wsmethod, topics
from wsutils.broker import Broker
from .constants import *
from . import utils


@wsmethod.wsMethod(coin=COIN_SYMBOL)
def subscribeToAddressBalance(subscriber, id, params, network):

    logger.printInfo(f"Executing WS method subscribeAddressBalance with id {id} and params {params}")

    requestSchema = utils.getWSRequestMethodSchema(SUBSCRIBE_ADDRESS_BALANCE)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    return subscriber.subscribeToTopic(
        broker=Broker(),
        topic=topics.Topic(
            name=f"{COIN_SYMBOL}{topics.TOPIC_SEPARATOR}{network}{topics.TOPIC_SEPARATOR}{topics.ADDRESS_BALANCE_TOPIC}"
                 f"{topics.TOPIC_SEPARATOR}{params['address']}",
            closingHandler=utils.closingAddrBalanceTopic
        )
    )


@wsmethod.wsMethod(coin=COIN_SYMBOL)
def unsubscribeFromAddressBalance(subscriber, id, params, network):

    logger.printInfo(f"Executing WS method unsubscribeAddressBalance with id {id} and params {params}")

    requestSchema = utils.getWSRequestMethodSchema(UNSUBSCRIBE_ADDRESS_BALANCE)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    return subscriber.unsubscribeFromTopic(
        broker=Broker(),
        topicName=f"{COIN_SYMBOL}{topics.TOPIC_SEPARATOR}{network}{topics.TOPIC_SEPARATOR}{topics.ADDRESS_BALANCE_TOPIC}"
                  f"{topics.TOPIC_SEPARATOR}{params['address']}"
    )


@wsmethod.wsMethod(coin=COIN_SYMBOL)
def subscribeToNewBlocks(subscriber, id, params, network):

    logger.printInfo(f"Executing WS method subscribeToNewBlock with id {id} and params {params}")

    requestSchema = utils.getWSRequestMethodSchema(SUBSCRIBE_TO_NEW_BLOCKS)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    return subscriber.subscribeToTopic(
        broker=Broker(),
        topic=topics.Topic(
            name=f"{COIN_SYMBOL}{topics.TOPIC_SEPARATOR}{network}{topics.TOPIC_SEPARATOR}{topics.NEW_BLOCKS_TOPIC}",
            closingHandler=None
        )
    )


@wsmethod.wsMethod(coin=COIN_SYMBOL)
def unsubscribeFromNewBlocks(subscriber, id, params, network):

    logger.printInfo(f"Executing WS method unsubscribeToNewBlockMine with id {id} and params {params}")

    requestSchema = utils.getWSRequestMethodSchema(UNSUBSCRIBE_FROM_NEW_BLOCKS)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    return subscriber.unsubscribeFromTopic(
        broker=Broker(),
        topicName=f"{COIN_SYMBOL}{topics.TOPIC_SEPARATOR}{network}{topics.TOPIC_SEPARATOR}{topics.NEW_BLOCKS_TOPIC}"
    )
