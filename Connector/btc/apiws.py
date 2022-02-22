#!/usr/bin/python3
from logger import logger
from httputils import httputils
from wsutils import wsmethod, topics
from wsutils.broker import Broker
from rpcutils import error
from . import apirpc, utils
from .constants import *


@wsmethod.wsMethod(coin=COIN_SYMBOL)
def subscribeToAddressBalance(subscriber, id, params, config):

    logger.printInfo(f"Executing WS method subscribeToAddressBalance with id {id} and params {params}")

    requestSchema = utils.getWSRequestMethodSchema(SUBSCRIBE_ADDRESS_BALANCE)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    broker = Broker()
    addrBalanceTopic = f"{COIN_SYMBOL}{topics.TOPIC_SEPARATOR}" \
                       f"{config.networkName}{topics.TOPIC_SEPARATOR}" \
                       f"{topics.ADDRESS_BALANCE_TOPIC}{topics.TOPIC_SEPARATOR}" \
                       f"{params['address']}"

    topic = topics.Topic(name=addrBalanceTopic, closingHandler=utils.closeAddrBalanceTopic)

    if not broker.isTopic(addrBalanceTopic):

        response = apirpc.notify(
            id=id,
            params={
                "address": params["address"],
                "callBackEndpoint": f"{config.bitcoinAddressCallbackHost}/{COIN_SYMBOL}/{config.networkName}"
                                    f"/callback/{ADDR_BALANCE_CALLBACK_NAME}"
            },
            config=config
        )

        if not response["success"]:
            logger.printError(f"Can not subscribe {params['address']} to node")
            raise error.RpcBadRequestError(f"Can not subscribe {params['address']} to node")

    return subscriber.subscribeToTopic(broker=broker, topic=topic)


@wsmethod.wsMethod(coin=COIN_SYMBOL)
def unsubscribeFromAddressBalance(subscriber, id, params, config):

    logger.printInfo(f"Executing WS method unsubscribeFromAddressBalance with id {id} and params {params}")

    requestSchema = utils.getWSRequestMethodSchema(UNSUBSCRIBE_ADDRESS_BALANCE)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    broker = Broker()
    addrBalanceTopic = f"{COIN_SYMBOL}{topics.TOPIC_SEPARATOR}" \
                       f"{config.networkName}{topics.ADDRESS_BALANCE_TOPIC}" \
                       f"{topics.TOPIC_SEPARATOR}{params['address']}"

    unsubscribeResponse = subscriber.unsubscribeFromTopic(broker=broker, topicName=addrBalanceTopic)

    if not broker.isTopic(addrBalanceTopic):

        response = apirpc.notify(
            id=id,
            params={
                "address": params['address'],
                "callBackEndpoint": ""
            },
            config=config
        )

        if not response["success"]:
            logger.printError(f"Can not unsubscribe {params['address']} to node")
            raise error.RpcBadRequestError(f"Can not unsubscribe {params['address']} to node")

    return unsubscribeResponse


@wsmethod.wsMethod(coin=COIN_SYMBOL)
def subscribeToNewBlocks(subscriber, id, params, config):

    logger.printInfo(f"Executing WS method subscribeToNewBlocks with id {id} and params {params}")

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


@wsmethod.wsMethod(coin=COIN_SYMBOL)
def unsubscribeFromNewBlocks(subscriber, id, params, config):

    logger.printInfo(f"Executing WS method unsubscribeFromNewBlocks with id {id} and params {params}")

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
