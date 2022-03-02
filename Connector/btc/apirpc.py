#!/usr/bin/python3
from httputils import httpmethod, httputils
from rpcutils import rpcmethod
from logger import logger
from rpcutils import error
from rpcutils.rpcconnector import RPCConnector
from . import utils
from .constants import *


@rpcmethod.rpcMethod(coin=COIN_SYMBOL)
@httpmethod.postHttpMethod(coin=COIN_SYMBOL)
def getAddressHistory(id, params, config):

    logger.printInfo(f"Executing RPC method getAddressHistory with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESS_HISTORY)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    addrHistory = RPCConnector.request(
        endpoint=config.electrumRpcEndpoint,
        id=id,
        method=GET_ADDRESS_HISTORY_METHOD,
        params=[params["address"]]
    )

    response = {
        "address": params["address"],
        "txHashes": []
    }

    for item in addrHistory:
        response["txHashes"].append(item["tx_hash"])

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    return response


@rpcmethod.rpcMethod(coin=COIN_SYMBOL)
@httpmethod.postHttpMethod(coin=COIN_SYMBOL)
def getAddressesHistory(id, params, config):

    logger.printInfo(
        f"Executing RPC method getAddressesHistory with id {id} and params {params}"
    )

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESSES_HISTORY)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    response = []

    for address in params["addresses"]:
        response.append(
            getAddressHistory(
                id,
                {
                    "address": address
                },
                config=config
            )
        )

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    return response


@rpcmethod.rpcMethod(coin=COIN_SYMBOL)
@httpmethod.postHttpMethod(coin=COIN_SYMBOL)
def getAddressBalance(id, params, config):

    logger.printInfo(f"Executing RPC method getAddressBalance with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESS_BALANCE)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    connResponse = RPCConnector.request(
        endpoint=config.electrumRpcEndpoint,
        id=id,
        method=GET_ADDRESS_BALANCE_METHOD,
        params=[params["address"]]
    )

    response = {
        "address": params["address"],
        "balance": {
            "confirmed": utils.convertToSatoshi(connResponse["confirmed"]),
            "unconfirmed": utils.convertToSatoshi(connResponse["unconfirmed"])
        }
    }

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    return response


@rpcmethod.rpcMethod(coin=COIN_SYMBOL)
@httpmethod.postHttpMethod(coin=COIN_SYMBOL)
def getAddressesBalance(id, params, config):

    logger.printInfo(f"Executing RPC method getAddressesBalance with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESSES_BALANCE)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

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
        raise error.RpcBadRequestError(id=id, message=err.message)

    return response


@rpcmethod.rpcMethod(coin=COIN_SYMBOL)
@httpmethod.postHttpMethod(coin=COIN_SYMBOL)
def getAddressUnspent(id, params, config):

    logger.printInfo(f"Executing RPC method getAddressUnspent with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESS_UNSPENT)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    connResponse = RPCConnector.request(
        endpoint=config.electrumRpcEndpoint,
        id=id,
        method=GET_ADDRESS_UNSPENT_METHOD,
        params=[params["address"]])

    response = []

    for tx in connResponse:

        response.append({
            "txHash": tx["tx_hash"],
            "vout": str(tx["tx_pos"]),
            "status": {
                "confirmed": tx["height"] != 0,
                "blockHeight": str(tx["height"])
            },
            "value": str(tx["value"])
        })

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    return response


@rpcmethod.rpcMethod(coin=COIN_SYMBOL)
@httpmethod.postHttpMethod(coin=COIN_SYMBOL)
def getAddressesUnspent(id, params, config):

    logger.printInfo(
        f"Executing RPC method getAddressesUnspent with id {id} and params {params}"
    )

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESSES_UNSPENT)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    response = []

    for address in params["addresses"]:

        response.append({
            "address": address,
            "outputs": getAddressUnspent(
                id=id,
                params={
                    "address": address
                },
                config=config
            )
        })

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

    logger.printInfo(f"Executing RPC method getBlockByHash with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_BLOCK_BY_HASH)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    block = RPCConnector.request(
        endpoint=config.bitcoincoreRpcEndpoint,
        id=id,
        method=GET_BLOCK_METHOD,
        params=[
            params["blockHash"],
            VERBOSITY_MORE_MODE
        ]
    )

    err = httputils.validateJSONSchema(block, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    return block


@rpcmethod.rpcMethod(coin=COIN_SYMBOL)
@httpmethod.postHttpMethod(coin=COIN_SYMBOL)
def getBlockByNumber(id, params, config):

    logger.printInfo(f"Executing RPC method getBlockByNumber with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_BLOCK_BY_NUMBER)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    blockHash = RPCConnector.request(
        endpoint=config.bitcoincoreRpcEndpoint,
        id=id,
        method=GET_BLOCK_HASH_METHOD,
        params=[params["blockNumber"]]
    )

    return getBlockByHash(
        id=id,
        params={"blockHash": blockHash},
        config=config
    )


@rpcmethod.rpcMethod(coin=COIN_SYMBOL)
@httpmethod.postHttpMethod(coin=COIN_SYMBOL)
def getFeePerByte(id, params, config):

    logger.printInfo(f"Executing RPC method getFeePerByte with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_FEE_PER_BYTE)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    feePerByte = RPCConnector.request(
        endpoint=config.bitcoincoreRpcEndpoint,
        id=id,
        method=ESTIMATE_SMART_FEE_METHOD,
        params=[params["confirmations"]]
    )

    if "feerate" not in feePerByte:
        logger.printError("Response without feerate field. No fee rate found")
        raise error.RpcInternalServerError(id=id, message="Response without feerate field. No fee rate found")

    response = {"feePerByte": utils.convertKbToBytes(utils.convertToSatoshi(feePerByte["feerate"]))}

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    return response


@rpcmethod.rpcMethod(coin=COIN_SYMBOL)
@httpmethod.postHttpMethod(coin=COIN_SYMBOL)
def getHeight(id, params, config):

    logger.printInfo(
        f"Executing RPC method getHeight with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_HEIGHT)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    latestBlockHeight = int(
        RPCConnector.request(
            endpoint=config.bitcoincoreRpcEndpoint,
            id=id,
            method=GET_BLOCK_COUNT_METHOD,
            params=[]
        )
    )
    latestBlockHash = RPCConnector.request(
        endpoint=config.bitcoincoreRpcEndpoint,
        id=id,
        method=GET_BLOCK_HASH_METHOD,
        params=[latestBlockHeight]
    )

    response = {
        "latestBlockIndex": str(latestBlockHeight),
        "latestBlockHash": latestBlockHash
    }

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    return response


"""Returns raw transaction (hex)"""


@rpcmethod.rpcMethod(coin=COIN_SYMBOL)
@httpmethod.postHttpMethod(coin=COIN_SYMBOL)
def getTransactionHex(id, params, config):

    logger.printInfo(f"Executing RPC method getTransactionHex with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_TRANSACTION_HEX)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    rawTransaction = RPCConnector.request(
        endpoint=config.bitcoincoreRpcEndpoint,
        id=id,
        method=GET_RAW_TRANSACTION_METHOD,
        params=[params["txHash"]]
    )

    response = {"rawTransaction": rawTransaction["hex"]}

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    return response


@rpcmethod.rpcMethod(coin=COIN_SYMBOL)
@httpmethod.postHttpMethod(coin=COIN_SYMBOL)
def getTransaction(id, params, config):
    logger.printInfo(f"Executing RPC method getTransaction with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_TRANSACTION)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    try:
        transaction = RPCConnector.request(
            endpoint=config.bitcoincoreRpcEndpoint,
            id=id,
            method=GET_RAW_TRANSACTION_METHOD,
            params=[
                params["txHash"],
                True
            ]
        )

        # Check if transaction is confirmed, and obtain block number
        if "blockhash" in transaction:
            transactionBlock = RPCConnector.request(
                endpoint=config.bitcoincoreRpcEndpoint,
                id=id,
                method=GET_BLOCK,
                params=[transaction["blockhash"], 1]
            )
            blockNumber = transactionBlock["height"]
        else:
            blockNumber = None

        transactionDetails = utils.decodeTransactionDetails(transaction, config.bitcoincoreRpcEndpoint)

        # Converting all transaction details to str
        transactionDetails["fee"] = str(transactionDetails["fee"])
        for input in transactionDetails["inputs"]:
            input["amount"] = str(input["amount"])
        for output in transactionDetails["outputs"]:
            output["amount"] = str(output["amount"])

        response = {
            "transaction": {
                "txId": transaction["txid"],
                "txHash": transaction["hash"],
                "blockNumber": str(blockNumber) if blockNumber is not None else blockNumber,
                "fee": transactionDetails["fee"],
                "inputs": transactionDetails["inputs"],
                "outputs": transactionDetails["outputs"],
                "data": transaction
            }
        }

    except error.RpcBadRequestError as err:
        logger.printError(f"Transaction {params['txHash']} could not be retrieve: {err}")
        return {"transaction": None}

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
def getAddressTransactionCount(id, params, config):

    logger.printInfo(f"Executing RPC method getAddressTransactionCount with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESS_TRANSACTION_COUNT)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    txs = RPCConnector.request(
        endpoint=config.electrumRpcEndpoint,
        id=id,
        method=GET_ADDRESS_HISTORY_METHOD,
        params=[params["address"]]
    )

    pending = 0
    for tx in txs:
        if tx["height"] == 0:
            pending += 1

    response = {
        "address": params["address"],
        "transactionCount": str(pending) if params["pending"] else str(len(txs) - pending)
    }

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    return response


@rpcmethod.rpcMethod(coin=COIN_SYMBOL)
@httpmethod.postHttpMethod(coin=COIN_SYMBOL)
def getAddressesTransactionCount(id, params, config):

    logger.printInfo(f"Executing RPC method getAddressesTransactionCount with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESSES_TRANSACTION_COUNT)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

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
        raise error.RpcBadRequestError(id=id, message=err.message)

    return transactionCounts


@rpcmethod.rpcMethod(coin=COIN_SYMBOL)
@httpmethod.postHttpMethod(coin=COIN_SYMBOL)
def broadcastTransaction(id, params, config):

    logger.printInfo(f"Executing RPC method broadcastTransaction with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(BROADCAST_TRANSACTION)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    hash = RPCConnector.request(
        endpoint=config.bitcoincoreRpcEndpoint,
        id=id,
        method=SEND_RAW_TRANSACTION_METHOD,
        params=[params["rawTransaction"]]
    )

    if hash is None:
        logger.printError(f"Transaction could not be broadcasted. Raw Transaction: {params['rawTransaction']}")
        raise error.RpcBadRequestError(id=id, message="Transaction could not be broadcasted")

    response = {
        "broadcasted": hash
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
def notify(id, params, config):

    logger.printInfo(f"Executing RPC method notify with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(NOTIFY)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    payload = RPCConnector.request(
        endpoint=config.electrumRpcEndpoint,
        id=id,
        method=NOTIFY_METHOD,
        params=[
            params["address"],
            params["callBackEndpoint"]
        ]
    )

    response = {"success": payload}

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    return response


@rpcmethod.rpcMethod(coin=COIN_SYMBOL)
@httpmethod.postHttpMethod(coin=COIN_SYMBOL)
def syncing(id, params, config):

    logger.printInfo(
        f"Executing RPC method syncing with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(SYNCING)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    blockchainInfo = RPCConnector.request(
        endpoint=config.bitcoincoreRpcEndpoint,
        id=id,
        method=GET_BLOCKCHAIN_INFO,
        params=None
    )

    if blockchainInfo is None:
        logger.printWarning("Could not get blockchain info from node")
        raise error.RpcBadRequestError(id=id, message="Could not get blockchain info from node")

    if blockchainInfo["blocks"] != blockchainInfo["headers"]:
        response = {
            "syncing": True,
            "syncPercentage": f"{str(blockchainInfo['verificationprogess']*100)}%",
            "currentBlockIndex": str(blockchainInfo["blocks"]),
            "latestBlockIndex": str(blockchainInfo["headers"]),
        }
    else:
        response = {"syncing": False}

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    return response
