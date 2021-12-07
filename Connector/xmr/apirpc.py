from .constants import *
from .connector import RPC_ENDPOINT
from rpcutils import rpcutils, errorhandler as rpcerrorhandler
from rpcutils.rpcconnector import RPCConnector
from . import utils
from logger import logger


@rpcutils.rpcMethod
def syncing(id, params):

    logger.printInfo(f"Executing RPC method syncing with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(SYNCING)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    blockchainInfo = RPCConnector.request(RPC_ENDPOINT, id, GET_INFO, None)

    if blockchainInfo is None:
        logger.printWarning("Could not get blockchain info from node")
        raise rpcerrorhandler.BadRequestError("Could not get blockchain info from node")

    if not blockchainInfo[SYNCHRONIZED]:
        syncInfo = RPCConnector.request(RPC_ENDPOINT, id, GET_SYNC_INFO, None)

        if syncInfo is None:
            logger.printWarning("Could not get syncing info from node")
            raise rpcerrorhandler.BadRequestError("Could not get syncing info from node")

        response = {
            SYNCING: True,
            SYNC_PERCENTAGE:
            f'{str(syncInfo[HEIGHT] / syncInfo[TARGET_HEIGHT] * 100)}%',
            CURRENT_BLOCK_INDEX: str(syncInfo[HEIGHT]),
            LATEST_BLOCK_INDEX: str(syncInfo[TARGET_HEIGHT]),
        }
    else:
        response = {SYNCING: False}

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response
