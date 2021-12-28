#!/usr/bin/python3
from httputils import httputils
from logger import logger
from rpcutils.rpcconnector import RPCConnector
from rpcutils import rpcutils, errorhandler as rpcerrorhandler
from .constants import *
from .connector import RPC_ENDPOINT
from . import utils


@httputils.postMethod
@rpcutils.rpcMethod
def getAddressBalance(id, params):

    logger.printInfo(
        f"Executing RPC method getAddressBalance with id {id} and params {params}"
    )

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESS_BALANCE)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    connLatest = RPCConnector.request(
        RPC_ENDPOINT, id, GET_BALANCE_METHOD,
        [utils.ensureHash(params[ADDRESS]), LATEST])
    connPending = RPCConnector.request(
        RPC_ENDPOINT, id, GET_BALANCE_METHOD,
        [utils.ensureHash(params[ADDRESS]), PENDING])

    response = {
        ADDRESS: params[ADDRESS],
        BALANCE: {
            CONFIRMED: utils.toWei(connPending),
            UNCONFIRMED: utils.toWei(connPending) - utils.toWei(connLatest, 16)
        }
    }

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response


@httputils.postMethod
@rpcutils.rpcMethod
def getAddressesBalance(id, params):

    logger.printInfo(
        f"Executing RPC method getAddressesBalance with id {id} and params {params}"
    )

    requestSchema, responseSchema = utils.getMethodSchemas(
        GET_ADDRESSES_BALANCE)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    response = []
    for address in params[ADDRESSES]:

        response.append(
            getAddressBalance(
                id,
                {
                    ADDRESS: address
                }
            )
        )

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response


@httputils.getMethod
@rpcutils.rpcMethod
def getHeight(id, params):

    logger.printInfo(
        f"Executing RPC method getHeight with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_HEIGHT)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    latestHash = RPCConnector.request(RPC_ENDPOINT, id,
                                      GET_BLOCK_BY_NUMBER_METHOD,
                                      [LATEST, True])

    response = {
        LATEST_BLOCK_INDEX: int(latestHash[NUMBER], 16),
        LATEST_BLOCK_HASH: latestHash[HASH]
    }

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response


@httputils.postMethod
@rpcutils.rpcMethod
def broadcastTransaction(id, params):

    logger.printInfo(
        f"Executing RPC method broadcastTransaction with id {id} and params {params}"
    )

    requestSchema, responseSchema = utils.getMethodSchemas(
        BROADCAST_TRANSACTION)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    transactionHash = RPCConnector.request(RPC_ENDPOINT, id,
                                           SEND_RAW_TRANSACTION_METHOD,
                                           [params[RAW_TRANSACTION]])
    response = {BROADCASTED: transactionHash}

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response


""" Data Structure: Transaction trie. Records transaction request vectors. """


@httputils.postMethod
@rpcutils.rpcMethod
def getTransaction(id, params):

    logger.printInfo(
        f"Executing RPC method getTransaction with id {id} and params {params}"
    )

    requestSchema, responseSchema = utils.getMethodSchemas(GET_TRANSACTION)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    transaction = RPCConnector.request(RPC_ENDPOINT, id,
                                       GET_TRANSACTION_BY_HASH_METHOD,
                                       [params[TX_HASH]])

    if transaction is None:
        logger.printWarning("Could not get transaction from node")
        raise rpcerrorhandler.BadRequestError("Could not get transaction from node")

    inputs = []
    outputs = []

    inputs.append({ADDRESS: transaction[FROM], AMOUNT: int(transaction[VALUE], 16)})
    outputs.append({ADDRESS: transaction[TO], AMOUNT: int(transaction[VALUE], 16)})

    response = {TRANSACTION: transaction, INPUTS: inputs, OUTPUTS: outputs}

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response


@httputils.postMethod
@rpcutils.rpcMethod
def getBlockByHash(id, params):

    logger.printInfo(
        f"Executing RPC method getBlockByHash with id {id} and params {params}"
    )

    requestSchema, responseSchema = utils.getMethodSchemas(GET_BLOCK_BY_HASH)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    block = RPCConnector.request(RPC_ENDPOINT, id, GET_BLOCK_BY_HASH_METHOD,
                                 [params[BLOCK_HASH], True])

    if block is None:
        raise rpcerrorhandler.BadRequestError(f"Block with hash {params[BLOCK_HASH]} could not be retrieve from node")

    response = {
        TRANSACTIONS: block[TRANSACTIONS]
    }

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response


@httputils.postMethod
@rpcutils.rpcMethod
def getTransactionCount(id, params):

    logger.printInfo(
        f"Executing RPC method getTransactionCount with id {id} and params {params}"
    )

    requestSchema, responseSchema = utils.getMethodSchemas(
        GET_TRANSACTION_COUNT)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    count = RPCConnector.request(RPC_ENDPOINT, id,
                                 GET_TRANSACTION_COUNT_METHOD, [
                                     utils.ensureHash(params[ADDRESS]),
                                     PENDING if params[PENDING] else LATEST
                                 ])

    response = {TRANSACTION_COUNT: int(count, 16)}

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response


@httputils.getMethod
@rpcutils.rpcMethod
def getGasPrice(id, params):

    logger.printInfo(
        f"Executing RPC method getGasPrice with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_GAS_PRICE)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    gas = RPCConnector.request(RPC_ENDPOINT, id, GET_GAS_PRICE_METHOD, None)

    response = {GAS_PRICE: utils.toWei(gas)}

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response


@httputils.postMethod
@rpcutils.rpcMethod
def estimateGas(id, params):

    logger.printInfo(
        f"Executing RPC method estimateGas with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(ESTIMATE_GAS)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    gas = RPCConnector.request(RPC_ENDPOINT, id, ESTIMATE_GAS_METHOD,
                               [params[TX]])

    response = {ESTIMATED_GAS: utils.toWei(gas)}

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response


""" Data Structure: Transaction receipt trie. Records the transaction outcome.
Receipts stores information that results from executing the transaction. I.e: The transaction receipt
contains information that is only available once a transaction has been executed in a block Adding
"cumulativeGasUsed", "contractAddress", "logs" and "logsBloom" """


@httputils.postMethod
@rpcutils.rpcMethod
def getTransactionReceipt(id, params):

    logger.printInfo(
        f"Executing RPC method getTransactionReceipt with id {id} and params {params}"
    )

    requestSchema, responseSchema = utils.getMethodSchemas(
        GET_TRANSACTION_RECEIPT)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    response = RPCConnector.request(RPC_ENDPOINT, id,
                                    GET_TRANSACTION_RECEIPT_METHOD,
                                    [params[TX_HASH]])

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response


@httputils.postMethod
@rpcutils.rpcMethod
def getBlockByNumber(id, params):

    logger.printInfo(
        f"Executing RPC method getBlockByNumber with id {id} and params {params}"
    )

    requestSchema, responseSchema = utils.getMethodSchemas(GET_BLOCK_BY_NUMBER)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    if isinstance(params[BLOCK_NUMBER], int):
        blockNumber = hex(params[BLOCK_NUMBER])
    elif not params[BLOCK_NUMBER].startswith('0x'):
        blockNumber = hex(int(params[BLOCK_NUMBER]))
    else:
        blockNumber = params[BLOCK_NUMBER]

    block = RPCConnector.request(RPC_ENDPOINT, id, GET_BLOCK_BY_NUMBER_METHOD,
                                 [blockNumber, True])

    if block is None:
        raise rpcerrorhandler.BadRequestError(f"Block number {blockNumber} could not be retrieve from node")

    response = {
        TRANSACTIONS: block[TRANSACTIONS]
    }

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response


@httputils.getMethod
@rpcutils.rpcMethod
def syncing(id, params):

    logger.printInfo(
        f"Executing RPC method syncing with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(SYNCING)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    sync = RPCConnector.request(RPC_ENDPOINT, id, SYNCING_METHOD, None)
    if sync is None:
        logger.printWarning("Could not get sync info from node")
        raise rpcerrorhandler.BadRequestError(
            "Could not get sync info from node")

    if not sync:
        response = {SYNCING: False}
    else:
        syncPercentage = utils.getSyncPercentage(int(sync[CURRENT_BLOCK], 16),
                                                 int(sync[HIGHEST_BLOCK], 16))

        response = {
            SYNCING: True,
            SYNC_PERCENTAGE: f"{syncPercentage}%",
            CURRENT_BLOCK_INDEX: int(sync[CURRENT_BLOCK], 16),
            LATEST_BLOCK_INDEX: int(sync[HIGHEST_BLOCK], 16),
        }

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response
