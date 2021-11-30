from .constants import *
from .connector import RPC_CORE_ENDPOINT, RPC_ELECTRUM_CASH_ENDPOINT
from rpcutils import rpcutils, errorhandler as rpcerrorhandler
from rpcutils.rpcconnector import RPCConnector
from . import utils
from logger import logger


@rpcutils.rpcMethod
def getAddressHistory(id, params):

    logger.printInfo(
        f"Executing RPC method getAddressHistory with id {id} and params {params}"
    )

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESS_HISTORY)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    addrHistory = RPCConnector.request(RPC_ELECTRUM_CASH_ENDPOINT, id,
                                       GET_ADDRESS_HISTORY_METHOD,
                                       [params[ADDRESS]])

    response = {TX_HASHES: []}

    for item in addrHistory:
        response[TX_HASHES].append(item[TX_HASH_SNAKE_CASE])

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response


@rpcutils.rpcMethod
def getAddressBalance(id, params):

    logger.printInfo(
        f"Executing RPC method getAddressBalance with id {id} and params {params}"
    )

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESS_BALANCE)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    connResponse = RPCConnector.request(RPC_ELECTRUM_CASH_ENDPOINT, id,
                                        GET_ADDRESS_BALANCE_METHOD,
                                        [params[ADDRESS]])

    response = {
        CONFIRMED: utils.convertToSatoshi(connResponse[CONFIRMED]),
        UNCONFIRMED: utils.convertToSatoshi(connResponse[UNCONFIRMED])
    }

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response


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

        addrBalance = getAddressBalance(id, {ADDRESS: address})

        response.append({ADDRESS: address, BALANCE: addrBalance})

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response


@rpcutils.rpcMethod
def getAddressUnspent(id, params):

    logger.printInfo(
        f"Executing RPC method getAddressUnspent with id {id} and params {params}"
    )

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESS_UNSPENT)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    connResponse = RPCConnector.request(RPC_ELECTRUM_CASH_ENDPOINT, id,
                                        GET_ADDRESS_UNSPENT_METHOD,
                                        [params[ADDRESS]])

    response = []

    for tx in connResponse:

        response.append({
            TX_HASH: tx[TX_HASH_SNAKE_CASE],
            VOUT: str(tx[TX_POS_SNAKE_CASE]),
            STATUS: {
                CONFIRMED: tx[HEIGHT] != 0,
                BLOCK_HEIGHT: str(tx[HEIGHT])
            },
            VALUE: str(tx[VALUE])
        })

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response


@rpcutils.rpcMethod
def getBlockByHash(id, params):

    logger.printInfo(f"Executing RPC method getBlockByHash with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_BLOCK_BY_HASH)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    block = RPCConnector.request(RPC_CORE_ENDPOINT, id, GET_BLOCK_METHOD, [params[BLOCK_HASH], VERBOSITY_MORE_MODE])

    err = rpcutils.validateJSONRPCSchema(block, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return block


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

    blockHash = RPCConnector.request(RPC_CORE_ENDPOINT, id, GET_BLOCK_HASH_METHOD, [blockNumber])

    return getBlockByHash(id, {BLOCK_HASH: blockHash})


@rpcutils.rpcMethod
def getFeePerByte(id, params):

    logger.printInfo(f"Executing RPC method getFeePerByte with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_FEE_PER_BYTE)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    try:
        confirmations = int(params[CONFIRMATIONS], base=10)
    except ValueError as err:
        raise rpcerrorhandler.BadRequestError(str(err))

    feePerByte = RPCConnector.request(RPC_CORE_ENDPOINT, id,
                                      ESTIMATE_SMART_FEE_METHOD,
                                      [confirmations])

    response = {FEE_PER_BYTE: utils.convertToSatoshi(feePerByte[FEE_RATE])}

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response


@rpcutils.rpcMethod
def getHeight(id, params):

    logger.printInfo(f"Executing RPC method getHeight with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_HEIGHT)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    latestBlockHeight = int(
        RPCConnector.request(RPC_CORE_ENDPOINT, id, GET_BLOCK_COUNT_METHOD,
                             []))
    latestBlockHash = RPCConnector.request(RPC_CORE_ENDPOINT, id,
                                           GET_BLOCK_HASH_METHOD,
                                           [latestBlockHeight])

    response = {
        LATEST_BLOCK_INDEX: latestBlockHeight,
        LATEST_BLOCK_HASH: latestBlockHash
    }

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response


"""Returns raw transaction (hex)"""


@rpcutils.rpcMethod
def getTransactionHex(id, params):

    logger.printInfo(f"Executing RPC method getTransactionHex with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_TRANSACTION_HEX)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    rawTransaction = RPCConnector.request(RPC_ELECTRUM_CASH_ENDPOINT, id,
                                          GET_TRANSACTION_METHOD,
                                          [params[TX_HASH]])

    response = {RAW_TRANSACTION: rawTransaction}

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response


@rpcutils.rpcMethod
def getTransaction(id, params):

    logger.printInfo(f"Executing RPC method getTransaction with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_TRANSACTION)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    transactionRaw = RPCConnector.request(RPC_ELECTRUM_CASH_ENDPOINT, id, GET_TRANSACTION_METHOD, [params[TX_HASH]])
    transaction = RPCConnector.request(RPC_CORE_ENDPOINT, id, DECODE_RAW_TRANSACTION_METHOD, [transactionRaw])

    err = rpcutils.validateJSONRPCSchema(transaction, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return transaction


@rpcutils.rpcMethod
def getTransactionCount(id, params):

    logger.printInfo(f"Executing RPC method getTransactionCount with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(
        GET_TRANSACTION_COUNT)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    txs = RPCConnector.request(RPC_ELECTRUM_CASH_ENDPOINT, id,
                               GET_ADDRESS_HISTORY_METHOD, [params[ADDRESS]])

    pending = 0
    for tx in txs:
        if tx[HEIGHT] == 0:
            pending += 1

    response = {
        TRANSACTION_COUNT:
        str(pending) if params[PENDING] else str(len(txs) - pending)
    }

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response


@rpcutils.rpcMethod
def broadcastTransaction(id, params):

    logger.printInfo(
        f"Executing RPC method broadcastTransaction with id {id} and params {params}"
    )

    requestSchema = utils.getRequestMethodSchema(BROADCAST_TRANSACTION)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    RPCConnector.request(RPC_CORE_ENDPOINT, id, SEND_RAW_TRANSACTION_METHOD, [params[RAW_TRANSACTION]])

    return {}


@rpcutils.rpcMethod
def syncing(id, params):

    logger.printInfo(f"Executing RPC method syncing with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(SYNCING)

    err = rpcutils.validateJSONRPCSchema(params, requestSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    blockchainInfo = RPCConnector.request(RPC_CORE_ENDPOINT, id,
                                          GET_BLOCKCHAIN_INFO, None)

    if blockchainInfo is None:
        logger.printWarning("Could not get blockchain info from node")
        raise rpcerrorhandler.BadRequestError(
            "Could not get blockchain info from node")

    if blockchainInfo[BLOCKS] != blockchainInfo[HEADERS]:
        response = {
            SYNCING: True,
            SYNC_PERCENTAGE:
            f'{str(blockchainInfo[VERIFICATION_PROGRESS]*100)}%',
            CURRENT_BLOCK_INDEX: blockchainInfo[BLOCKS],
            LATEST_BLOCK_INDEX: blockchainInfo[HEADERS],
        }
    else:
        response = {SYNCING: False}

    err = rpcutils.validateJSONRPCSchema(response, responseSchema)
    if err is not None:
        raise rpcerrorhandler.BadRequestError(err.message)

    return response
