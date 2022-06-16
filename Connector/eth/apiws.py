#!/usr/bin/python3
from logger import logger
from httputils import httputils
from rpcutils import error
from wsutils import topics
from wsutils.wsmethod import RouteTableDef
from wsutils.broker import Broker
from .constants import *
from . import utils


@RouteTableDef.ws(currency=COIN_SYMBOL)
async def subscribeToAddressBalance(subscriber, id, params, config):

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
            name=f"{COIN_SYMBOL}{topics.TOPIC_SEPARATOR}"
                 f"{config.networkName}{topics.TOPIC_SEPARATOR}"
                 f"{topics.ADDRESS_BALANCE_TOPIC}{topics.TOPIC_SEPARATOR}"
                 f"{params['address']}",
            closingHandler=None
        )
    )


@RouteTableDef.ws(currency=COIN_SYMBOL)
async def unsubscribeFromAddressBalance(subscriber, id, params, config):

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
        topicName=f"{COIN_SYMBOL}{topics.TOPIC_SEPARATOR}{config.networkName}{topics.TOPIC_SEPARATOR}{topics.ADDRESS_BALANCE_TOPIC}"
                  f"{topics.TOPIC_SEPARATOR}{params['address']}"
    )


@RouteTableDef.ws(currency=COIN_SYMBOL)
async def subscribeToNewBlocks(subscriber, id, params, config):

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
            name=f"{COIN_SYMBOL}{topics.TOPIC_SEPARATOR}"
                 f"{config.networkName}{topics.TOPIC_SEPARATOR}"
                 f"{topics.NEW_BLOCKS_TOPIC}",
            closingHandler=None
        )
    )


@RouteTableDef.ws(currency=COIN_SYMBOL)
async def unsubscribeFromNewBlocks(subscriber, id, params, config):

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
        topicName=f"{COIN_SYMBOL}{topics.TOPIC_SEPARATOR}{config.networkName}{topics.TOPIC_SEPARATOR}{topics.NEW_BLOCKS_TOPIC}"
    )
