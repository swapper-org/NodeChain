from .constants import *
from .connector import RPC_ENDPOINT
from rpcutils import rpcutils, errorhandler as rpcerrorhandler
from rpcutils.rpcconnector import RPCConnector
from . import utils
from logger import logger


@rpcutils.rpcMethod
def getAddressBalance(id, params):

    logger.printInfo(
        f"Executing RPC method getAddressBalance with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESS_BALANCE)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    connLatest = RPCConnector.request(RPC_ENDPOINT, id, GET_BALANCE_METHOD, [
                                      utils.ensureHash(params[ADDRESS]), LATEST])
    connPending = RPCConnector.request(RPC_ENDPOINT, id, GET_BALANCE_METHOD, [
                                       utils.ensureHash(params[ADDRESS]), PENDING])

    response = {
        CONFIRMED: connPending,
        UNCONFIRMED: hex(int(connPending, 16) - int(connLatest, 16))
    }

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response


@rpcutils.rpcMethod
def getAddressesBalance(id, params):

    logger.printInfo(
        f"Executing RPC method getAddressesBalance with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(
        GET_ADDRESSES_BALANCE)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    response = []
    for address in params[ADDRESSES]:

        balance = getAddressBalance(
            id,
            {
                ADDRESS: address
            }
        )
        response.append(
            {
                ADDRESS: address,
                BALANCE: balance
            }
        )

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response


@rpcutils.rpcMethod
def getHeight(id, params):

    logger.printInfo(
        f"Executing RPC method getHeight with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_HEIGHT)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    latestHash = RPCConnector.request(
        RPC_ENDPOINT, id, GET_BLOCK_BY_NUMBER_METHOD, [LATEST, True])

    response = {
        LATEST_BLOCK_INDEX: latestHash[NUMBER],
        LATEST_BLOCK_HASH: latestHash[HASH]
    }

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response


@rpcutils.rpcMethod
def broadcastTransaction(id, params):

    logger.printInfo(
        f"Executing RPC method broadcastTransaction with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(
        BROADCAST_TRANSACTION)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    transactionHash = RPCConnector.request(
        RPC_ENDPOINT, id, SEND_RAW_TRANSACTION_METHOD, [params[RAW_TRANSACTION]])
    response = {
        BROADCASTED: transactionHash
    }

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response


""" Data Structure: Transaction trie. Records transaction request vectors. """


@rpcutils.rpcMethod
def getTransaction(id, params):

    logger.printInfo(
        f"Executing RPC method getTransaction with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_TRANSACTION)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    transaction = RPCConnector.request(
        RPC_ENDPOINT, id, GET_TRANSACTION_BY_HASH_METHOD, [params[TX_HASH]])

    if transaction is None:
        logger.printWarning("Could not get transaction from node")
        raise rpcerrorhandler.BadRequestError(
            "Could not get transaction from node")

    inputs = []
    outputs = []

    inputs.append(
        {
            ADDRESS: transaction[FROM],
            AMOUNT: transaction[VALUE]
        }
    )
    outputs.append(
        {
            ADDRESS: transaction[TO],
            AMOUNT: transaction[VALUE]
        }
    )

    response = {
        TRANSACTION: transaction,
        INPUTS: inputs,
        OUTPUTS: outputs
    }

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response


@rpcutils.rpcMethod
def getBlockByHash(id, params):

    logger.printInfo(
        f"Executing RPC method getBlockByHash with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_BLOCK_BY_HASH)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    block = RPCConnector.request(RPC_ENDPOINT, id, GET_BLOCK_BY_HASH_METHOD, [
                                 params[BLOCK_HASH], True])

    response = {
        TRANSACTIONS: block[TRANSACTIONS]
    }

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response


@rpcutils.rpcMethod
def getTransactionCount(id, params):

    logger.printInfo(
        f"Executing RPC method getTransactionCount with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(
        GET_TRANSACTION_COUNT)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    count = RPCConnector.request(RPC_ENDPOINT, id, GET_TRANSACTION_COUNT_METHOD, [
                                 utils.ensureHash(params[ADDRESS]), PENDING if params[PENDING] else LATEST])

    response = {
        TRANSACTION_COUNT: count
    }

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response


@rpcutils.rpcMethod
def getGasPrice(id, params):

    logger.printInfo(
        f"Executing RPC method getGasPrice with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_GAS_PRICE)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    gas = RPCConnector.request(RPC_ENDPOINT, id, GET_GAS_PRICE_METHOD, None)

    response = {
        GAS_PRICE: gas
    }

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response


@rpcutils.rpcMethod
def estimateGas(id, params):

    logger.printInfo(
        f"Executing RPC method estimateGas with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(ESTIMATE_GAS)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    gas = RPCConnector.request(
        RPC_ENDPOINT, id, ESTIMATE_GAS_METHOD, [params[TX]])

    response = {
        ESTIMATED_GAS: gas
    }

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response


""" Data Structure: Transaction receipt trie. Records the transaction outcome.
Receipts stores information that results from executing the transaction. I.e: The transaction receipt
contains information that is only available once a transaction has been executed in a block Adding
"cumulativeGasUsed", "contractAddress", "logs" and "logsBloom" """


@rpcutils.rpcMethod
def getTransactionReceipt(id, params):

    logger.printInfo(
        f"Executing RPC method getTransactionReceipt with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(
        GET_TRANSACTION_RECEIPT)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    response = RPCConnector.request(
        RPC_ENDPOINT, id, GET_TRANSACTION_RECEIPT_METHOD, [params[TX_HASH]])

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response


@rpcutils.rpcMethod
def getBlockByNumber(id, params):

    logger.printInfo(
        f"Executing RPC method getBlockByNumber with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_BLOCK_BY_NUMBER)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    if not params[BLOCK_NUMBER].startswith('0x'):
        blockNumber = hex(int(params[BLOCK_NUMBER]))
    else:
        blockNumber = params[BLOCK_NUMBER]

    block = RPCConnector.request(
        RPC_ENDPOINT, id, GET_BLOCK_BY_NUMBER_METHOD, [blockNumber, True])

    response = {
        TRANSACTIONS: block[TRANSACTIONS]
    }

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response
