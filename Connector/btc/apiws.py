from .constants import *
from .connector import BITCOIN_CALLBACK_ENDPOINT
from wsutils import wsutils
from wsutils.broker import Broker
from wsutils import topics
from rpcutils import rpcutils, errorhandler as rpcerrorhandler
from . import apirpc
from . import utils
from logger import logger


@wsutils.webSocketMethod
def subscribeAddressBalance(subscriber, id, params):

    logger.printInfo(f"Executing WS method subscribeAddressBalance with id {id} and params {params}")

    requestSchema = utils.getWSRequestMethodSchema(SUBSCRIBE_ADDRESS_BALANCE)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    broker = Broker()
    addrBalanceTopic = topics.ADDRESS_BALANCE_TOPIC + topics.TOPIC_SEPARATOR + params[ADDRESS]

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

    return subscriber.subscribeToTopic(broker, addrBalanceTopic)


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
