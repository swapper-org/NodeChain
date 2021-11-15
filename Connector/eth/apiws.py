from .constants import *
from wsutils import wsutils
from wsutils.subscriptionshandler import SubcriptionsHandler
from rpcutils import rpcutils, errorhandler as rpcerrorhandler
from . import utils
from logger import logger


@wsutils.webSocketMethod
def subscribeAddressBalance(ws, id, params):

    logger.printInfo(f"Executing WS method subscribeAddressBalance with id {id} and params {params}")

    requestSchema = utils.getWSRequestMethodSchema(SUBSCRIBE_ADDRESS_BALANCE)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return SubcriptionsHandler.subscribe(
        utils.ensureHash(params[ADDRESS]),
        ws
    )


@wsutils.webSocketMethod
def unsubscribeAddressBalance(ws, id, params):

    logger.printInfo(f"Executing WS method unsubscribeAddressBalance with id {id} and params {params}")

    requestSchema = utils.getWSRequestMethodSchema(UNSUBSCRIBE_ADDRESS_BALANCE)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return SubcriptionsHandler.unsubscribe(
        utils.ensureHash(params[ADDRESS]),
        ws
    )
