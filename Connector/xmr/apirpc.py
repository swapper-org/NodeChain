from httputils import httputils
from .constants import *
from .connector import RPC_ENDPOINT
from rpcutils import rpcutils, errorhandler as rpcerrorhandler
from rpcutils.rpcconnector import RPCConnector
from . import utils
from logger import logger


@httputils.getMethod
@rpcutils.rpcMethod
def getFeePerByte(id, params):
    logger.printInfo(f"Executing RPC method getFeePerByte with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_FEE_PER_BYTE)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    fee = RPCConnector.request(RPC_ENDPOINT, id, GET_FEE_ESTIMATE_METHOD, None)

    if fee is None:
        logger.printWarning("Could not get fee info from node")
        raise rpcerrorhandler.BadRequestError("Could not get fee info from node")

    response = {
        FEE_PER_BYTE: fee[FEE]
    }

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response


@httputils.postMethod
@rpcutils.rpcMethod
def getBlockByNumber(id, params):
    logger.printInfo(f"Executing RPC method getBlockByNumber with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_BLOCK_BY_NUMBER)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    try:
        blockNumber = int(params[BLOCK_NUMBER], base=10)
    except Exception as err:
        raise rpcerrorhandler.BadRequestError(str(err))

    block = RPCConnector.request(RPC_ENDPOINT, id, GET_BLOCK_METHOD, [blockNumber])

    if block is None:
        logger.printWarning("Could not get block info from node")
        raise rpcerrorhandler.BadRequestError("Could not get block info from node")

    err = rpcutils.validateJSONRPCSchema(block, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return block


@httputils.postMethod
@rpcutils.rpcMethod
def getBlockByHash(id, params):
    logger.printInfo(f"Executing RPC method getBlockByHash with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_BLOCK_BY_HASH)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    block = RPCConnector.request(RPC_ENDPOINT, id, GET_BLOCK_METHOD, [params[BLOCK_HASH]])

    if block is None:
        logger.printWarning("Could not get block info from node")
        raise rpcerrorhandler.BadRequestError("Could not get block info from node")

    err = rpcutils.validateJSONRPCSchema(block, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return block


@httputils.getMethod
@rpcutils.rpcMethod
def getHeight(id, params):
    logger.printInfo(f"Executing RPC method getHeight with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_HEIGHT)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    blockchainInfo = RPCConnector.request(RPC_ENDPOINT, id, GET_INFO_METHOD, None)

    if blockchainInfo is None:
        logger.printWarning("Could not get latest blockchain info from node")
        raise rpcerrorhandler.BadRequestError("Could not get latest blockchain info from node")

    response = {
        LATEST_BLOCK_INDEX: blockchainInfo[HEIGHT],
        LATEST_BLOCK_HASH: blockchainInfo[TOP_BLOCK_HASH]
    }

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response


# @rpcutils.rpcMethod
# def checkTxProof(id, params):
#     logger.printInfo(f"Executing RPC method checkTxProof with id {id} and params {params}")

#     requestSchema, responseSchema = utils.getMethodSchemas(CHECK_TX_PROOF)

#     err = rpcutils.validateJSONRPCSchema(params, requestSchema)
#     if err is not None:
#         raise rpcerrorhandler.BadRequestError(err.message)

#     blockchainInfo = RPCConnector.request(RPC_ENDPOINT, id, GET_INFO_METHOD, None)

#     if blockchainInfo is None:
#         logger.printWarning("Could not get blockchain info from node")
#         raise rpcerrorhandler.BadRequestError("Could not get blockchain info from node")


#     return response


# @rpcutils.rpcMethod
# def checkSpendProof(id, params):
#     logger.printInfo(f"Executing RPC method checkSpendProof with id {id} and params {params}")

#     requestSchema, responseSchema = utils.getMethodSchemas(CHECK_SPEND_PROOF)

#     err = rpcutils.validateJSONRPCSchema(params, requestSchema)
#     if err is not None:
#         raise rpcerrorhandler.BadRequestError(err.message)

#     blockchainInfo = RPCConnector.request(RPC_ENDPOINT, id, GET_INFO_METHOD, None)

#     return response


@httputils.getMethod
@rpcutils.rpcMethod
def syncing(id, params):
    logger.printInfo(f"Executing RPC method syncing with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(SYNCING)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    blockchainInfo = RPCConnector.request(RPC_ENDPOINT, id, GET_INFO_METHOD, None)

    if blockchainInfo is None:
        logger.printWarning("Could not get blockchain info from node")
        raise rpcerrorhandler.BadRequestError("Could not get blockchain info from node")

    if not blockchainInfo[SYNCHRONIZED]:
        syncInfo = RPCConnector.request(RPC_ENDPOINT, id, GET_SYNC_INFO_METHOD, None)

        if syncInfo is None:
            logger.printWarning("Could not get syncing info from node")
            raise rpcerrorhandler.BadRequestError("Could not get syncing info from node")

        response = {
            SYNCING: True,
            SYNC_PERCENTAGE:
            f'{str(syncInfo[HEIGHT] / syncInfo[TARGET_HEIGHT] * 100)}%',
            CURRENT_BLOCK_INDEX: str(syncInfo[HEIGHT]),
            LATEST_BLOCK: str(syncInfo[TARGET_HEIGHT]),
        }
    else:
        response = {SYNCING: False}

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response
