#!/usr/bin/python3
from httputils import httpmethod, httputils, error as httpError
from httputils.httpconnector import HTTPConnector
from rpcutils import rpcmethod, error
from rpcutils.rpcconnector import RPCConnector
from logger import logger
from .constants import *
from . import utils


@rpcmethod.rpcMethod(coin=COIN_SYMBOL)
@httpmethod.postHttpMethod(coin=COIN_SYMBOL)
def getAddressBalance(id, params, config):

    logger.printInfo(
        f"Executing RPC method getAddressBalance with id {id} and params {params}"
    )

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESS_BALANCE)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    connLatest = RPCConnector.request(
        endpoint=config.rpcEndpoint,
        id=id,
        method=GET_BALANCE_METHOD,
        params=[
            utils.ensureHash(params["address"]),
            "latest"
        ]
    )

    connPending = RPCConnector.request(
        endpoint=config.rpcEndpoint,
        id=id,
        method=GET_BALANCE_METHOD,
        params=[
            utils.ensureHash(params["address"]),
            "pending"
        ]
    )

    response = {
        "address": params["address"],
        "balance": {
            "confirmed": str(utils.toWei(connPending)),
            "unconfirmed": str(utils.toWei(connPending) - utils.toWei(connLatest))
        }
    }

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    return response


@rpcmethod.rpcMethod(coin=COIN_SYMBOL)
@httpmethod.postHttpMethod(coin=COIN_SYMBOL)
def getAddressesBalance(id, params, config):

    logger.printInfo(
        f"Executing RPC method getAddressesBalance with id {id} and params {params}"
    )

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESSES_BALANCE)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    response = []
    for address in params["addresses"]:

        response.append(
            getAddressBalance(
                id=id,
                params={
                    "address": address
                },
                config=config
            )
        )

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    return response


@rpcmethod.rpcMethod(coin=COIN_SYMBOL)
@httpmethod.postHttpMethod(coin=COIN_SYMBOL)
def getHeight(id, params, config):

    logger.printInfo(
        f"Executing RPC method getHeight with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_HEIGHT)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    latestHash = RPCConnector.request(
        endpoint=config.rpcEndpoint,
        id=id,
        method=GET_BLOCK_BY_NUMBER_METHOD,
        params=[
            "latest",
            True
        ]
    )

    response = {
        "latestBlockIndex": str(int(latestHash["number"], 16)),
        "latestBlockHash": latestHash["hash"]
    }

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    return response


@rpcmethod.rpcMethod(coin=COIN_SYMBOL)
@httpmethod.postHttpMethod(coin=COIN_SYMBOL)
def broadcastTransaction(id, params, config):

    logger.printInfo(
        f"Executing RPC method broadcastTransaction with id {id} and params {params}"
    )

    requestSchema, responseSchema = utils.getMethodSchemas(BROADCAST_TRANSACTION)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    transactionHash = RPCConnector.request(
        endpoint=config.rpcEndpoint,
        id=id,
        method=SEND_RAW_TRANSACTION_METHOD,
        params=[
            params["rawTransaction"]
        ]
    )
    response = {"broadcasted": transactionHash}

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    return response


"""
Data Structure: Transaction trie. Records transaction request vectors.
"""


@rpcmethod.rpcMethod(coin=COIN_SYMBOL)
@httpmethod.postHttpMethod(coin=COIN_SYMBOL)
def getTransaction(id, params, config):

    logger.printInfo(
        f"Executing RPC method getTransaction with id {id} and params {params}"
    )

    requestSchema, responseSchema = utils.getMethodSchemas(GET_TRANSACTION)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    transaction = RPCConnector.request(
        endpoint=config.rpcEndpoint,
        id=id,
        method=GET_TRANSACTION_BY_HASH_METHOD,
        params=[
            params["txHash"]
        ]
    )

    if transaction is None:
        logger.printWarning("Could not get transaction from node")
        return {"transaction": None}

    response = {
        "transaction": {
            "txHash": params["txHash"],
            "fee": str(utils.toWei(transaction["gasPrice"]) * utils.toWei(transaction["gas"])),
            "blockHash": transaction["blockHash"],
            "blockNumber": str(int(transaction["blockNumber"], 16)) if transaction["blockNumber"] is not None else None,
            "data": transaction,
            "inputs": [
                {
                    "address": transaction["from"],
                    "amount": str(utils.toWei(transaction["value"]))
                }
            ],
            "outputs": [
                {
                    "address": transaction["to"],
                    "amount": str(utils.toWei(transaction["value"]))
                }
            ]
        }
    }

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    return response


@rpcmethod.rpcMethod(coin=COIN_SYMBOL)
@httpmethod.postHttpMethod(coin=COIN_SYMBOL)
def getTransactions(id, params, config):

    logger.printInfo(f"Executing RPC method getTransactions with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_TRANSACTIONS)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    response = {
        "transactions": []
    }

    for txHash in params["txHashes"]:
        response["transactions"].append(
            getTransaction(
                id=id,
                params={
                    "txHash": txHash
                },
                config=config
            )
        )

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    return response


@rpcmethod.rpcMethod(coin=COIN_SYMBOL)
@httpmethod.postHttpMethod(coin=COIN_SYMBOL)
def getBlockByHash(id, params, config):

    logger.printInfo(
        f"Executing RPC method getBlockByHash with id {id} and params {params}"
    )

    requestSchema, responseSchema = utils.getMethodSchemas(GET_BLOCK_BY_HASH)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    block = RPCConnector.request(
        endpoint=config.rpcEndpoint,
        id=id,
        method=GET_BLOCK_BY_HASH_METHOD,
        params=[
            params["blockHash"],
            True
        ]
    )

    if block is None:
        raise error.RpcBadRequestError(
            id=id,
            message=f"Block with hash {params['blockHash']} could not be retrieve from node")

    err = httputils.validateJSONSchema(block, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    return block


@rpcmethod.rpcMethod(coin=COIN_SYMBOL)
@httpmethod.postHttpMethod(coin=COIN_SYMBOL)
def getAddressTransactionCount(id, params, config):

    logger.printInfo(
        f"Executing RPC method getAddressTransactionCount with id {id} and params {params}"
    )

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESS_TRANSACTION_COUNT)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    count = RPCConnector.request(
        endpoint=config.rpcEndpoint,
        id=id,
        method=GET_TRANSACTION_COUNT_METHOD,
        params=[
            utils.ensureHash(params["address"]),
            "pending" if params["pending"] else "latest"
        ]
    )

    response = {
        "address": params["address"],
        "transactionCount": str(int(count, 16))
    }

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    return response


@rpcmethod.rpcMethod(coin=COIN_SYMBOL)
@httpmethod.postHttpMethod(coin=COIN_SYMBOL)
def getAddressesTransactionCount(id, params, config):

    logger.printInfo(
        f"Executing RPC method getAddressesTransactionCount with id {id} and params {params}"
    )

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESSES_TRANSACTION_COUNT)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    transactionCounts = []
    for address in params["addresses"]:
        transactionCounts.append(
            getAddressTransactionCount(
                id=id,
                params=address,
                config=config
            )
        )

    err = httputils.validateJSONSchema(transactionCounts, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    return transactionCounts


@rpcmethod.rpcMethod(coin=COIN_SYMBOL)
@httpmethod.postHttpMethod(coin=COIN_SYMBOL)
def getGasPrice(id, params, config):

    logger.printInfo(
        f"Executing RPC method getGasPrice with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_GAS_PRICE)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    gas = RPCConnector.request(
        endpoint=config.rpcEndpoint,
        id=id,
        method=GET_GAS_PRICE_METHOD,
        params=None
    )

    response = {"gasPrice": str(utils.toWei(gas))}

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    return response


@rpcmethod.rpcMethod(coin=COIN_SYMBOL)
@httpmethod.postHttpMethod(coin=COIN_SYMBOL)
def estimateGas(id, params, config):

    logger.printInfo(
        f"Executing RPC method estimateGas with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(ESTIMATE_GAS)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    gas = RPCConnector.request(
        endpoint=config.rpcEndpoint,
        id=id,
        method=ESTIMATE_GAS_METHOD,
        params=[
            params["tx"]
        ]
    )

    response = {"estimatedGas": str(utils.toWei(gas))}

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    return response


"""
Data Structure: Transaction receipt trie. Records the transaction outcome.
Receipts stores information that results from executing the transaction. I.e: The transaction receipt
contains information that is only available once a transaction has been executed in a block Adding
"cumulativeGasUsed", "contractAddress", "logs" and "logsBloom"
"""


@rpcmethod.rpcMethod(coin=COIN_SYMBOL)
@httpmethod.postHttpMethod(coin=COIN_SYMBOL)
def getTransactionReceipt(id, params, config):

    logger.printInfo(
        f"Executing RPC method getTransactionReceipt with id {id} and params {params}"
    )

    requestSchema, responseSchema = utils.getMethodSchemas(GET_TRANSACTION_RECEIPT)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    response = RPCConnector.request(
        endpoint=config.rpcEndpoint,
        id=id,
        method=GET_TRANSACTION_RECEIPT_METHOD,
        params=[
            params["txHash"]
        ]
    )

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    return response


@rpcmethod.rpcMethod(coin=COIN_SYMBOL)
@httpmethod.postHttpMethod(coin=COIN_SYMBOL)
def getBlockByNumber(id, params, config):

    logger.printInfo(
        f"Executing RPC method getBlockByNumber with id {id} and params {params}"
    )

    requestSchema, responseSchema = utils.getMethodSchemas(GET_BLOCK_BY_NUMBER)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    if isinstance(params["blockNumber"], int):
        blockNumber = hex(params["blockNumber"])
    elif not params["blockNumber"].startswith('0x'):
        blockNumber = hex(int(params["blockNumber"]))
    else:
        blockNumber = params["blockNumber"]

    block = RPCConnector.request(
        endpoint=config.rpcEndpoint,
        id=id,
        method=GET_BLOCK_BY_NUMBER_METHOD,
        params=[blockNumber, True]
    )

    if block is None:
        raise error.RpcBadRequestError(
            id=id,
            message=f"Block number {blockNumber} could not be retrieve from node"
        )

    err = httputils.validateJSONSchema(block, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    return block


@rpcmethod.rpcMethod(coin=COIN_SYMBOL)
@httpmethod.postHttpMethod(coin=COIN_SYMBOL)
def syncing(id, params, config):

    logger.printInfo(
        f"Executing RPC method syncing with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(SYNCING)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    sync = RPCConnector.request(
        endpoint=config.rpcEndpoint,
        id=id,
        method=SYNCING_METHOD,
        params=None
    )

    if sync is None:
        logger.printWarning("Could not get sync info from node")
        raise error.RpcBadRequestError(
            id=id,
            message="Could not get sync info from node"
        )

    if not sync:
        response = {"syncing": False}
    else:
        syncPercentage = utils.getSyncPercentage(int(sync["currentBlock"], 16),
                                                 int(sync["highestBlock"], 16))

        response = {
            "syncing": True,
            "syncPercentage": f"{syncPercentage}%",
            "currentBlockIndex": str(int(sync["currentBlock"], 16)),
            "latestBlockIndex": str(int(sync["highestBlock"], 16)),
        }

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    return response


@rpcmethod.rpcMethod(coin=COIN_SYMBOL)
@httpmethod.postHttpMethod(coin=COIN_SYMBOL)
def call(id, params, config):

    logger.printInfo(
        f"Executing RPC method call with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(CALL)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    result = RPCConnector.request(
        endpoint=config.rpcEndpoint,
        id=id,
        method=CALL_METHOD,
        params=[
            {
                "to": params["transaction"]["to"],
                "from": params["transaction"]["from"] if "from" in params["transaction"] else None,
                "gasPrice": params["transaction"]["gasPrice"] if "gasPrice" in params["transaction"] else None,
                "gas": params["transaction"]["gas"] if "gas" in params["transaction"] else None,
                "value": params["transaction"]["value"] if "value" in params["transaction"] else None,
                "data": params["transaction"]["data"] if "data" in params["transaction"] else None
            },
            params["blockNumber"]
        ]
    )

    response = {
        "data": result
    }

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    return response


@rpcmethod.rpcMethod(coin=COIN_SYMBOL)
@httpmethod.postHttpMethod(coin=COIN_SYMBOL)
def getAddressHistory(id, params, config):

    logger.printInfo(
        f"Executing RPC method getAddressHistory with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESS_HISTORY)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    try:
        addrHistory = HTTPConnector.get(
            endpoint=f"{config.indexerEndpoint}",
            path=INDEXER_TXS_PATH,
            params={
                "and": f"(contract_to.eq.,or(txfrom.eq.{params['address']},txto.eq.{params['address']}))",
                "order": "time.desc"
            }
        )
    except httpError.Error as err:
        raise error.RpcError(
            id=id,
            message=err.message,
            code=err.code
        )

    response = {
        "address": params["address"],
        "txHashes": [tx["txhash"] for tx in addrHistory]
    }

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    return response


@rpcmethod.rpcMethod(coin=COIN_SYMBOL)
@httpmethod.postHttpMethod(coin=COIN_SYMBOL)
def getAddressesHistory(id, params, config):

    logger.printInfo(
        f"Executing RPC method getAddressesHistory with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESSES_HISTORY)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    response = []
    for address in params["addresses"]:
        response.append(
            getAddressHistory(
                id=id,
                params={
                    "address": address
                },
                config=config
            )
        )

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    return response
