#!/usr/bin/python3
import asyncio
import sys
import random
from httputils import httputils, error as httpError
from httputils.httpmethod import RouteTableDef as HttpRouteTableDef
from httputils.httpconnector import HTTPConnector
from rpcutils import error
from rpcutils.rpcmethod import RouteTableDef as RpcRouteTableDef
from rpcutils.rpcconnector import RPCConnector
from logger.logger import Logger
from .constants import *
from . import utils
from utils import utils as globalUtils


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL)
@HttpRouteTableDef.post(currency=COIN_SYMBOL)
async def getAddressBalance(id, params, config):

    Logger.printDebug(f"Executing RPC method getAddressBalance with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESS_BALANCE)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    connLatestTask = asyncio.ensure_future(
        RPCConnector.request(
            endpoint=config.rpcEndpoint,
            id=id,
            method=GET_BALANCE_METHOD,
            params=[
                utils.ensureHash(params["address"]),
                "latest"
            ]
        )
    )

    connPendingTask = asyncio.ensure_future(
        RPCConnector.request(
            endpoint=config.rpcEndpoint,
            id=id,
            method=GET_BALANCE_METHOD,
            params=[
                utils.ensureHash(params["address"]),
                "pending"
            ]
        )
    )

    connLatest = await connLatestTask
    connPending = await connPendingTask

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


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL)
@HttpRouteTableDef.post(currency=COIN_SYMBOL)
async def getAddressesBalance(id, params, config):

    Logger.printDebug(f"Executing RPC method getAddressesBalance with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESSES_BALANCE)

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
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    return response


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL)
@HttpRouteTableDef.get(currency=COIN_SYMBOL)
async def getHeight(id, params, config):

    Logger.printDebug(f"Executing RPC method getHeight with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_HEIGHT)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    latestHash = await RPCConnector.request(
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


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL)
@HttpRouteTableDef.post(currency=COIN_SYMBOL)
async def broadcastTransaction(id, params, config):

    Logger.printDebug(f"Executing RPC method broadcastTransaction with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(BROADCAST_TRANSACTION)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    transactionHash = await RPCConnector.request(
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

    Logger.printWarning("Broadcasted transaction in Ethereum network: " + str(hash))
    return response


"""
Data Structure: Transaction trie. Records transaction request vectors.
"""


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL)
@HttpRouteTableDef.post(currency=COIN_SYMBOL)
async def getTransaction(id, params, config):

    Logger.printDebug(f"Executing RPC method getTransaction with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_TRANSACTION)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    transaction = await RPCConnector.request(
        endpoint=config.rpcEndpoint,
        id=id,
        method=GET_TRANSACTION_BY_HASH_METHOD,
        params=[
            params["txHash"]
        ]
    )

    if transaction is None:
        Logger.printWarning(f"Could not get transaction {params['txHash']} from node")
        return {"transaction": None}

    blockNumber = timestamp = None
    if transaction["blockNumber"] is not None:
        blockNumber = transaction["blockNumber"]

        block = await getBlockByNumber(
            id=id,
            params={
                "blockNumber": blockNumber
            },
            config=config
        )

        timestamp = block["block"]["timestamp"]

    response = {
        "transaction": {
            "txHash": params["txHash"],
            "fee": str(utils.toWei(transaction["gasPrice"]) * utils.toWei(transaction["gas"])),
            "blockHash": transaction["blockHash"],
            "blockNumber": str(int(blockNumber, 16)) if blockNumber is not None else None,
            "timestamp": str(int(timestamp, 16)) if timestamp is not None else None,
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


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL)
@HttpRouteTableDef.post(currency=COIN_SYMBOL)
async def getTransactions(id, params, config):

    Logger.printDebug(f"Executing RPC method getTransactions with id {id} and params {params}")

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
async def getBlockByHash(id, params, config):

    Logger.printDebug(f"Executing RPC method getBlockByHash with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_BLOCK_BY_HASH)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    block = await RPCConnector.request(
        endpoint=config.rpcEndpoint,
        id=id,
        method=GET_BLOCK_BY_HASH_METHOD,
        params=[
            params["blockHash"],
            True if "verbosity" not in params else params["verbosity"] == VERBOSITY_MORE_MODE
        ]
    )

    if block is None:
        raise error.RpcBadRequestError(
            id=id,
            message=f"Block with hash {params['blockHash']} could not be retrieve from node")

    response = {"block": block}

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

    Logger.printDebug(f"Executing RPC method getAddressTransactionCount with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESS_TRANSACTION_COUNT)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    count = await RPCConnector.request(
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


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL)
@HttpRouteTableDef.post(currency=COIN_SYMBOL)
async def getAddressesTransactionCount(id, params, config):

    Logger.printDebug(f"Executing RPC method getAddressesTransactionCount with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESSES_TRANSACTION_COUNT)

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
                getAddressTransactionCount(
                    id=id,
                    params=address,
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
@HttpRouteTableDef.get(currency=COIN_SYMBOL)
async def getGasPrice(id, params, config):

    Logger.printDebug(f"Executing RPC method getGasPrice with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_GAS_PRICE)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    gas = await RPCConnector.request(
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


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL)
@HttpRouteTableDef.post(currency=COIN_SYMBOL)
async def estimateGas(id, params, config):

    Logger.printDebug(f"Executing RPC method estimateGas with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(ESTIMATE_GAS)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    gas = await RPCConnector.request(
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


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL)
@HttpRouteTableDef.post(currency=COIN_SYMBOL)
async def getTransactionReceipt(id, params, config):

    Logger.printDebug(f"Executing RPC method getTransactionReceipt with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_TRANSACTION_RECEIPT)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    response = await RPCConnector.request(
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


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL)
@HttpRouteTableDef.post(currency=COIN_SYMBOL)
async def getBlockByNumber(id, params, config):

    Logger.printDebug(f"Executing RPC method getBlockByNumber with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_BLOCK_BY_NUMBER)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    blockNumber = params["blockNumber"]

    if blockNumber != "latest" and not utils.isHexNumber(blockNumber):
        blockNumber = hex(int(blockNumber))

    block = await RPCConnector.request(
        endpoint=config.rpcEndpoint,
        id=id,
        method=GET_BLOCK_BY_NUMBER_METHOD,
        params=[
            blockNumber,
            True if "verbosity" not in params else params["verbosity"] == VERBOSITY_MORE_MODE
        ]
    )

    if block is None:
        raise error.RpcBadRequestError(
            id=id,
            message="Block could not be retrieved from node"
        )

    response = {"block": block}

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    return response


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL)
@HttpRouteTableDef.get(currency=COIN_SYMBOL)
async def syncing(id, params, config):

    Logger.printDebug(f"Executing RPC method syncing with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(SYNCING)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    sync = await RPCConnector.request(
        endpoint=config.rpcEndpoint,
        id=id,
        method=SYNCING_METHOD,
        params=None
    )

    if sync is None:
        Logger.printWarning("Could not get sync info from node")
        raise error.RpcBadGatewayError(
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


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL)
@HttpRouteTableDef.post(currency=COIN_SYMBOL)
async def call(id, params, config):

    Logger.printDebug(f"Executing RPC method call with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(CALL)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    result = await RPCConnector.request(
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


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL)
@HttpRouteTableDef.post(currency=COIN_SYMBOL)
async def getAddressHistory(id, params, config):

    Logger.printDebug(f"Executing RPC method getAddressHistory with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESS_HISTORY)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    if "status" not in params or params["status"] in ["pending", "all"]:
        pendingTask = asyncio.ensure_future(
            getAddressPendingTransactions(
                address=params["address"],
                config=config
            )
        )

    if "status" not in params or params["status"] in ["confirmed", "all"]:
        confirmedTask = asyncio.ensure_future(
            getAddressConfirmedTransactions(
                address=params["address"],
                config=config
            )
        )

    txs = []
    if 'pendingTask' in locals():
        txs += await pendingTask

    if 'confirmedTask' in locals():
        txs += await confirmedTask

    txs = globalUtils.removeDuplicates(txs)

    recentFirst = "order" not in params or params["order"] == "desc"

    paginatedTxs = globalUtils.paginate(
        elements=txs,
        page=params["page"] if "page" in params else None,
        pageSize=params["pageSize"] if "pageSize" in params else None,
        side="left" if recentFirst else "right"
    )

    response = {
        "address": params["address"],
        "txHashes": paginatedTxs if recentFirst else paginatedTxs[::-1],
        "maxPage": globalUtils.getMaxPage(
            numElements=len(txs),
            pageSize=params["pageSize"] if "pageSize" in params else None
        )
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
async def getAddressesHistory(id, params, config):

    Logger.printDebug(f"Executing RPC method getAddressesHistory with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESSES_HISTORY)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    _params = {param: params[param] for param in params if param != "addresses"}
    tasks = []

    for address in params["addresses"]:
        _params["address"] = address
        tasks.append(
            asyncio.ensure_future(
                getAddressHistory(
                    id=id,
                    params=dict(_params),
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


async def getAddressPendingTransactions(address, config):

    try:

        pendingTransactions = await HTTPConnector.post(
            endpoint=config.rpcEndpoint,
            path=GRAPHQL_PATH,
            data={
                "query": "query { pending { transactions { hash from { address } to { address } } } }"
            }
        )

    except httpError.Error:
        Logger.printError("Could not retrieve pending transactions using Graphql query")
        return []

    txs = []

    for tx in pendingTransactions["data"]["pending"]["transactions"]:
        if utils.isAddressInvolvedInTx(address=address, tx=tx):
            txs.append(tx["hash"])

    return txs


async def getAddressConfirmedTransactions(address, config):

    try:
        txs = await HTTPConnector.get(
            endpoint=config.indexerEndpoint,
            path=INDEXER_TXS_PATH,
            params={
                "and": f"(and(status.eq.true,or(txfrom.eq.{address},txto.eq.{address})))",
                "order": "time.desc"
            }
        )

    except httpError.Error as err:
        Logger.printError("Can not retrieve confirmed transactions")
        raise error.RpcError(
            id=random.randint(1, sys.maxsize),
            message=err.message,
            code=err.code
        )

    return [tx["txhash"] for tx in txs]


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL)
@HttpRouteTableDef.get(currency=COIN_SYMBOL)
async def indexing(id, params, config):

    Logger.printDebug(f"Executing RPC method indexing with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(INDEXING)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    try:

        indexerTask = HTTPConnector.get(
            endpoint=config.indexerEndpoint,
            path=INDEXER_MAX_BLOCK_PATH,
            headers={
                "Accept": "application/vnd.pgrst.object+json"
            }
        )

    except httpError.Error as err:
        raise error.RpcError(
            id=id,
            message=err.message,
            code=err.code
        )

    getHeightResponse = await getHeight(
        id=id,
        params={},
        config=config
    )

    indexerResponse = await indexerTask
    maxBlock = indexerResponse["max"] if indexerResponse["max"] is not None else 0

    percentage = utils.getSyncPercentage(
        maxBlock,
        int(getHeightResponse["latestBlockIndex"])
    )

    response = {
        "indexing": maxBlock != 0 and maxBlock != int(getHeightResponse["latestBlockIndex"]),
        "indexingPercentage": f"{percentage}%",
        "currentBlockIndex": str(maxBlock),
        "latestBlockIndex": str(int(getHeightResponse["latestBlockIndex"])),
    }

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    return response
