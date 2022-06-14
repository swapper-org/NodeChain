#!/usr/bin/python3
import asyncio
from httputils import httputils
from httputils.httpmethod import RouteTableDef as HttpRouteTableDef
from rpcutils.rpcmethod import RouteTableDef as RpcRouteTableDef
from logger import logger
from rpcutils import error
from rpcutils.rpcconnector import RPCConnector
from . import utils
from utils import utils as globalUtils
from .constants import *


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL)
@HttpRouteTableDef.post(currency=COIN_SYMBOL)
async def getAddressHistory(id, params, config):

    logger.printInfo(f"Executing RPC method getAddressHistory with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESS_HISTORY)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    addrHistory = await RPCConnector.request(
        endpoint=config.electrumRpcEndpoint,
        id=id,
        method=GET_ADDRESS_HISTORY_METHOD,
        params=[params["address"]]
    )

    txs = [item["tx_hash"] for item in addrHistory[::-1]]
    leftSide = "order" not in params or params["order"] == "desc"

    paginatedTxs = globalUtils.paginate(
        elements=txs,
        page=params["page"] if "page" in params else None,
        pageSize=params["pageSize"] if "pageSize" in params else None,
        side="left" if leftSide else "right"
    )

    response = {
        "address": params["address"],
        "txHashes": paginatedTxs if leftSide else paginatedTxs[::-1],
        "maxPage": globalUtils.getMaxPage(
            numElements=len(txs),
            pageSize=params["pageSize"] if "pageSize" in params else None
        )
    }

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    return response


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL)
@HttpRouteTableDef.post(currency=COIN_SYMBOL)
async def getAddressesHistory(id, params, config):

    logger.printInfo(
        f"Executing RPC method getAddressesHistory with id {id} and params {params}"
    )

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESSES_HISTORY)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    tasks = []

    for address in params["addresses"]:
        tasks.append(
            asyncio.ensure_future(
                getAddressHistory(
                    id,
                    {
                        "address": address
                    },
                    config=config
                )
            )
        )
    response = await asyncio.gather(*tasks)

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    return response


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL)
@HttpRouteTableDef.post(currency=COIN_SYMBOL)
async def getAddressBalance(id, params, config):

    logger.printInfo(f"Executing RPC method getAddressBalance with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESS_BALANCE)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    connResponse = await RPCConnector.request(
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


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL)
@HttpRouteTableDef.post(currency=COIN_SYMBOL)
async def getAddressesBalance(id, params, config):

    logger.printInfo(f"Executing RPC method getAddressesBalance with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESSES_BALANCE)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    tasks = []

    for address in params["addresses"]:
        tasks.append(
            asyncio.ensure_future(
                getAddressBalance(
                    id=id,
                    params={
                        "address": address
                    },
                    config=config
                )
            )
        )
    response = await asyncio.gather(*tasks)

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    return response


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL)
@HttpRouteTableDef.post(currency=COIN_SYMBOL)
async def getAddressUnspent(id, params, config):

    logger.printInfo(f"Executing RPC method getAddressUnspent with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESS_UNSPENT)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    connResponse = await RPCConnector.request(
        endpoint=config.electrumRpcEndpoint,
        id=id,
        method=GET_ADDRESS_UNSPENT_METHOD,
        params=[params["address"]])

    response = []

    for tx in connResponse:
        response.append({
            "address": params["address"],
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


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL)
@HttpRouteTableDef.post(currency=COIN_SYMBOL)
async def getAddressesUnspent(id, params, config):

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

    tasks = []

    for address in params["addresses"]:
        tasks.append(
            asyncio.ensure_future(
                getAddressUnspent(
                    id=id,
                    params={
                        "address": address
                    },
                    config=config
                )
            )
        )

    response = await asyncio.gather(*tasks)

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    return response


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL)
@HttpRouteTableDef.post(currency=COIN_SYMBOL)
async def getBlockByHash(id, params, config):

    logger.printInfo(f"Executing RPC method getBlockByHash with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_BLOCK_BY_HASH)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    block = await RPCConnector.request(
        endpoint=config.bitcoincoreRpcEndpoint,
        id=id,
        method=GET_BLOCK_METHOD,
        params=[
            params["blockHash"],
            params["verbosity"] if "verbosity" in params else VERBOSITY_MORE_MODE
        ]
    )

    response = {"block": block}

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    return response


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL)
@HttpRouteTableDef.post(currency=COIN_SYMBOL)
async def getBlockByNumber(id, params, config):

    logger.printInfo(f"Executing RPC method getBlockByNumber with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_BLOCK_BY_NUMBER)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    if params["blockNumber"] == "latest":

        blockHeight = getHeight(
            id=id,
            params={},
            config=config
        )
        blockHash = blockHeight["latestBlockHash"]

    else:

        blockHash = await RPCConnector.request(
            endpoint=config.bitcoincoreRpcEndpoint,
            id=id,
            method=GET_BLOCK_HASH_METHOD,
            params=[
                int(
                    params["blockNumber"],
                    (16 if utils.isHexNumber(params["blockNumber"]) else 10)
                )
            ]
        )

    return await getBlockByHash(
        id=id,
        params={
            "blockHash": blockHash,
            "verbosity": params["verbosity"] if "verbosity" in params else VERBOSITY_MORE_MODE
        },
        config=config
    )


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL)
@HttpRouteTableDef.post(currency=COIN_SYMBOL)
async def getFeePerByte(id, params, config):

    logger.printInfo(f"Executing RPC method getFeePerByte with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_FEE_PER_BYTE)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    feePerByte = await RPCConnector.request(
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


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL)
@HttpRouteTableDef.get(currency=COIN_SYMBOL)
async def getHeight(id, params, config):
    logger.printInfo(
        f"Executing RPC method getHeight with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_HEIGHT)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    latestBlockHeight = int(
        await RPCConnector.request(
            endpoint=config.bitcoincoreRpcEndpoint,
            id=id,
            method=GET_BLOCK_COUNT_METHOD,
            params=[]
        )
    )
    latestBlockHash = await RPCConnector.request(
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


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL)
@HttpRouteTableDef.post(currency=COIN_SYMBOL)
async def getTransactionHex(id, params, config):

    logger.printInfo(f"Executing RPC method getTransactionHex with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_TRANSACTION_HEX)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    rawTransaction = await RPCConnector.request(
        endpoint=config.bitcoincoreRpcEndpoint,
        id=id,
        method=GET_RAW_TRANSACTION_METHOD,
        params=[
            params["txHash"],
            False if "verbose" not in params else params["verbose"]
        ]
    )

    response = {"rawTransaction": rawTransaction}

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    return response


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL)
@HttpRouteTableDef.post(currency=COIN_SYMBOL)
async def getTransaction(id, params, config):

    logger.printInfo(f"Executing RPC method getTransaction with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_TRANSACTION)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    try:
        transaction = await getTransactionHex(
            id=id,
            params={
                "txHash": params["txHash"],
                "verbose": True
            },
            config=config
        )

        # Check if transaction is confirmed, and obtain block number
        blockNumber = timestamp = None
        if "blockhash" in transaction["rawTransaction"]:
            transactionBlock = await getBlockByHash(
                id=id,
                params={
                    "blockHash": transaction["rawTransaction"]["blockhash"],
                    "verbosity": VERBOSITY_DEFAULT_MODE
                },
                config=config
            )
            blockNumber = transactionBlock["block"]["height"]
            timestamp = transactionBlock["block"]["time"]

        transactionDetails = utils.decodeTransactionDetails(transaction["rawTransaction"], id, config)

        # Converting all transaction details to str

        for input in transactionDetails["inputs"]:
            input["amount"] = str(input["amount"])
        for output in transactionDetails["outputs"]:
            output["amount"] = str(output["amount"])

        response = {
            "transaction": {
                "txId": transaction["rawTransaction"]["txid"],
                "txHash": transaction["rawTransaction"]["hash"],
                "blockNumber": str(blockNumber) if blockNumber is not None else None,
                "timestamp": str(timestamp) if timestamp is not None else None,
                "fee": str(transactionDetails["fee"]),
                "inputs": transactionDetails["inputs"],
                "outputs": transactionDetails["outputs"],
                "data": transaction["rawTransaction"]
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


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL)
@HttpRouteTableDef.post(currency=COIN_SYMBOL)
async def getTransactions(id, params, config):

    logger.printInfo(f"Executing RPC method getTransactions with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_TRANSACTIONS)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    tasks = []

    for txHash in params["txHashes"]:
        tasks.append(
            asyncio.ensure_future(
                getTransaction(
                    id=id,
                    params={
                        "txHash": txHash
                    },
                    config=config
                )
            )
        )

    response = {
        "transactions": await asyncio.gather(*tasks)
    }

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    return response


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL)
@HttpRouteTableDef.post(currency=COIN_SYMBOL)
async def getAddressTransactionCount(id, params, config):

    logger.printInfo(f"Executing RPC method getAddressTransactionCount with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESS_TRANSACTION_COUNT)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    txs = await RPCConnector.request(
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


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL)
@HttpRouteTableDef.post(currency=COIN_SYMBOL)
async def getAddressesTransactionCount(id, params, config):

    logger.printInfo(f"Executing RPC method getAddressesTransactionCount with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESSES_TRANSACTION_COUNT)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    tasks = []

    for address in params["addresses"]:
        tasks.append(
            asyncio.ensure_future(
                getAddressTransactionCount(
                    id=id,
                    params=address,
                    config=config
                )
            )
        )

    transactionCounts = await asyncio.gather(*tasks)

    err = httputils.validateJSONSchema(transactionCounts, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    return transactionCounts


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL)
@HttpRouteTableDef.post(currency=COIN_SYMBOL)
async def broadcastTransaction(id, params, config):

    logger.printInfo(f"Executing RPC method broadcastTransaction with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(BROADCAST_TRANSACTION)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    hash = await RPCConnector.request(
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


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL)
@HttpRouteTableDef.post(currency=COIN_SYMBOL)
async def notify(id, params, config):

    logger.printInfo(f"Executing RPC method notify with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(NOTIFY)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    payload = await RPCConnector.request(
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


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL)
@HttpRouteTableDef.get(currency=COIN_SYMBOL)
async def syncing(id, params, config):

    logger.printInfo(
        f"Executing RPC method syncing with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(SYNCING)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    blockchainInfo = await RPCConnector.request(
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
            "syncPercentage": f"{str(blockchainInfo['verificationprogress']*100)}%",
            "currentBlockIndex": str(blockchainInfo["blocks"]),
            "latestBlockIndex": str(blockchainInfo["headers"]),
        }
    else:
        response = {"syncing": False}

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(id=id, message=err.message)

    return response
