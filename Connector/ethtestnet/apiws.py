from .constants import *
from wsutils import wsutils
from wsutils.subscriptionshandler import SubcriptionsHandler
from rpcutils import rpcutils, errorhandler as rpcerrorhandler
from . import utils


@wsutils.webSocketMethod
def subscribeAddressBalance(ws, id, params):

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

    requestSchema = utils.getWSRequestMethodSchema(UNSUBSCRIBE_ADDRESS_BALANCE)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return SubcriptionsHandler.unsubscribe(
        utils.ensureHash(params[ADDRESS]),
        ws
    )
