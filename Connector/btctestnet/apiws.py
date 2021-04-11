from .constants import *
from .connector import BITCOIN_CALLBACK_ENDPOINT
from wsutils import wsutils
from wsutils.subscriptionshandler import SubcriptionsHandler
from rpcutils import rpcutils, errorhandler as rpcerrorhandler
from . import apirpc
from . import utils


@wsutils.webSocketMethod
def subscribeAddressBalance(ws, id, params):

    requestSchema = utils.getWSRequestMethodSchema(SUBSCRIBE_ADDRESS_BALANCE)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    if not SubcriptionsHandler.addressHasClients(params[ADDRESS]):

        response = apirpc.notify(
            id,
            {
                ADDRESS: params[ADDRESS],
                CALLBACK_ENDPOINT: BITCOIN_CALLBACK_ENDPOINT
            }
        )

        if not response[SUCCESS]:
            raise rpcerrorhandler.BadRequestError("Can not subscribe " + params[ADDRESS] + " to node")

    return SubcriptionsHandler.subscribe(params[ADDRESS], ws)


@wsutils.webSocketMethod
def unsubscribeAddressBalance(ws, id, params):

    requestSchema = utils.getWSRequestMethodSchema(UNSUBSCRIBE_ADDRESS_BALANCE)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)


    unsubscribeResponse = SubcriptionsHandler.unsubscribe(params[ADDRESS], ws)

    if not SubcriptionsHandler.addressHasClients(params[ADDRESS]):

        response = apirpc.notify(
            id,
            {
                ADDRESS: params[ADDRESS],
                CALLBACK_ENDPOINT: ""
            }
        )

        if not response[SUCCESS]:
            raise rpcerrorhandler.BadRequestError("Can not unsubscribe " + params[ADDRESS] + " to node")

    return unsubscribeResponse
