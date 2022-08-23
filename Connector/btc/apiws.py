#!/usr/bin/python3
from logger.logger import Logger
from httputils import httputils
from wsutils import topics
from wsutils.wsmethod import RouteTableDef
from wsutils.broker import Broker
from rpcutils import error
from . import apirpc, utils
from .constants import *

"""
@RouteTableDef.ws(currency=COIN_SYMBOL)
async def subscribeToAddressBalance(subscriber, id, params, config):

    Logger.printDebug(f"Executing WS method subscribeToAddressBalance with id {id} and params {params}")

    requestSchema = utils.getWSRequestMethodSchema(SUBSCRIBE_ADDRESS_BALANCE)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    broker = Broker()
    addrBalanceTopic = f"{COIN_SYMBOL}{topics.TOPIC_SEPARATOR}" \
                       f"{config.networkName}{topics.TOPIC_SEPARATOR}" \
                       f"{topics.ADDRESS_BALANCE_TOPIC}{topics.TOPIC_SEPARATOR}" \
                       f"{params['address']}"

    topic = topics.Topic(
        name=addrBalanceTopic,
        closingHandler=utils.AddrBalanceTopicCloseHandler(topicName=addrBalanceTopic, config=config)
    )

    if not broker.isTopic(addrBalanceTopic):

        response = await apirpc.notify(
            id=id,
            params={
                "address": params["address"],
                "callBackEndpoint": f"{config.bitcoinAddressCallbackHost}/{COIN_SYMBOL}/{config.networkName}"
                                    f"/callback/{ADDR_BALANCE_CALLBACK_NAME}"
            },
            config=config
        )

        if not response["success"]:
            Logger.printError(f"Can not subscribe {params['address']} to node")
            raise error.RpcBadGatewayError(id=id)

    return subscriber.subscribeToTopic(broker=broker, topic=topic)


@RouteTableDef.ws(currency=COIN_SYMBOL)
async def unsubscribeFromAddressBalance(subscriber, id, params, config):

    Logger.printDebug(f"Executing WS method unsubscribeFromAddressBalance with id {id} and params {params}")

    requestSchema = utils.getWSRequestMethodSchema(UNSUBSCRIBE_ADDRESS_BALANCE)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    return subscriber.unsubscribeFromTopic(
        broker=Broker(),
        topicName=f"{COIN_SYMBOL}{topics.TOPIC_SEPARATOR}"
                  f"{config.networkName}{topics.TOPIC_SEPARATOR}"
                  f"{topics.ADDRESS_BALANCE_TOPIC}{topics.TOPIC_SEPARATOR}"
                  f"{params['address']}"
    )


@RouteTableDef.ws(currency=COIN_SYMBOL)
async def subscribeToNewBlocks(subscriber, id, params, config):

    Logger.printDebug(f"Executing WS method subscribeToNewBlocks with id {id} and params {params}")

    requestSchema = utils.getWSRequestMethodSchema(SUBSCRIBE_TO_NEW_BLOCKS)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

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

    Logger.printDebug(f"Executing WS method unsubscribeFromNewBlocks with id {id} and params {params}")

    responseSchema = utils.getWSRequestMethodSchema(UNSUBSCRIBE_FROM_NEW_BLOCKS)

    err = httputils.validateJSONSchema(params, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    return subscriber.unsubscribeFromTopic(
        broker=Broker(),
        topicName=f"{COIN_SYMBOL}{topics.TOPIC_SEPARATOR}"
                  f"{config.networkName}{topics.TOPIC_SEPARATOR}"
                  f"{topics.NEW_BLOCKS_TOPIC}"
    )
"""
