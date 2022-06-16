#!/usr/bin/python
import asyncio
from web3 import Web3
from rpcutils import error
from rpcutils.rpcmethod import RouteTableDef as RpcRouteTableDef
from httputils.httpmethod import RouteTableDef as HttpRouteTableDef
from eth import apirpc as ethapirpc, utils as ethutils
from eth.constants import COIN_SYMBOL, INDEXER_TXS_PATH, GRAPHQL_PATH
from httputils import httputils, error as httpError
from httputils.httpconnector import HTTPConnector
from logger import logger
from .constants import *
from . import utils
from utils import utils as globalutils


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL, standard=ERC20_STANDARD_SYMBOL)
@HttpRouteTableDef.post(currency=COIN_SYMBOL, standard=ERC20_STANDARD_SYMBOL)
async def getAddressBalance(id, params, config):

    logger.printInfo(f"Executing RPC method getAddressBalance with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESS_BALANCE)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    abi = utils.getFunctionABI(
        utils.getABISchema(BALANCE_OF_METHOD_ECR20_ABI)
    )

    contract = Web3().eth.contract(
        abi=[abi]
    )
    data = contract.encodeABI(
        fn_name=BALANCE_OF_METHOD_ECR20_ABI,
        args=[
            Web3().toChecksumAddress(params["address"])
        ]
    )

    response = {}

    for contractAddress in params["contractAddresses"]:

        result = await ethapirpc.call(
            id=id,
            params={
                "transaction": {
                    "to": contractAddress,
                    "data": data
                },
                "blockNumber": "latest"
            },
            config=config
        )

        response[contractAddress] = {
            "address": params["address"],
            "balance": {
                "confirmed": str(ethutils.toWei(result["data"])),
                "unconfirmed": "0"
            }
        }

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    return response


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL, standard=ERC20_STANDARD_SYMBOL)
@HttpRouteTableDef.post(currency=COIN_SYMBOL, standard=ERC20_STANDARD_SYMBOL)
async def getAddressesBalance(id, params, config):

    logger.printInfo(f"Executing RPC method getAddressBalance with id {id} and params {params}")

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
                        "address": address,
                        "contractAddresses": params["contractAddresses"]
                    },
                    config=config
                )
            )
        )

    response = {}
    for contractAddress in params["contractAddresses"]:
        response[contractAddress] = []

    originalResponses = await asyncio.gather(*tasks)

    for originalResponse in originalResponses:
        for contractAddress, addressBalance in originalResponse.items():
            response[contractAddress].append(addressBalance)

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    return response


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL, standard=ERC20_STANDARD_SYMBOL)
@HttpRouteTableDef.post(currency=COIN_SYMBOL, standard=ERC20_STANDARD_SYMBOL)
async def getTransaction(id, params, config):

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

    transaction = await ethapirpc.getTransaction(
        id=id,
        params=params,
        config=config
    )

    if not transaction["transaction"]:
        return transaction

    abi = utils.getFunctionABI(
        utils.getABISchema(TRANSFER_METHOD_ERC_20_ABI)
    )

    contract = Web3().eth.contract(
        address=Web3.toChecksumAddress(transaction["transaction"]["data"]["to"]),
        abi=[abi]
    )

    try:

        func_obj, func_params = contract.decode_function_input(transaction["transaction"]["data"]["input"])
        transaction["transaction"]["inputs"][0]["amount"] = str(func_params["_value"])
        transaction["transaction"]["outputs"][0]["address"] = func_params["_to"]
        transaction["transaction"]["outputs"][0]["amount"] = str(func_params["_value"])

    except ValueError as err:

        logger.printError(f"Can not decode transaction input. Transaction hash is not erc-20 transfer. {err}")
        raise error.RpcBadRequestError(
            id=id,
            message="Transaction input data not corresponding to erc-20 transfer"
        )

    err = httputils.validateJSONSchema(transaction, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    return transaction


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL, standard=ERC20_STANDARD_SYMBOL)
@HttpRouteTableDef.post(currency=COIN_SYMBOL, standard=ERC20_STANDARD_SYMBOL)
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


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL, standard=ERC20_STANDARD_SYMBOL)
@HttpRouteTableDef.post(currency=COIN_SYMBOL, standard=ERC20_STANDARD_SYMBOL)
async def getAddressHistory(id, params, config):

    logger.printInfo(f"Executing RPC method getAddressHistory with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESS_HISTORY)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    response = {}
    recentFirst = "order" not in params or params["order"] == "desc"

    for contractAddress in params["contractAddresses"]:

        if "status" not in params or params["status"] in ["pending", "all"]:
            pendingTask = getAddressPendingTransactions(
                address=params["address"],
                contractAddress=contractAddress,
                config=config
            )

        if "status" not in params or params["status"] in ["confirmed", "all"]:
            confirmedTask = getAddressConfirmedTransactions(
                address=params["address"],
                contractAddress=contractAddress,
                config=config
            )

        txs = []

        if pendingTask in locals():
            txs += await pendingTask

        if confirmedTask in locals():
            txs += await confirmedTask

        paginatedTxs = globalutils.paginate(
            elements=txs,
            page=params["page"] if "page" in params else None,
            pageSize=params["pageSize"] if "pageSize" in params else None,
            side="left" if recentFirst else "right"
        )

        response[contractAddress] = {
            "address": params["address"],
            "txHashes": paginatedTxs if recentFirst else paginatedTxs[::-1],
            "maxPage": globalutils.getMaxPage(
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


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL, standard=ERC20_STANDARD_SYMBOL)
@HttpRouteTableDef.post(currency=COIN_SYMBOL, standard=ERC20_STANDARD_SYMBOL)
async def getAddressesHistory(id, params, config):

    logger.printInfo(
        f"Executing RPC method getAddressesHistory with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESSES_HISTORY)

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
                getAddressHistory(
                    id=id,
                    params={
                        "address": address,
                        "contractAddresses": params["contractAddresses"]
                    },
                    config=config
                )
            )
        )

    response = {}

    for contractAddress in params["contractAddresses"]:
        response[contractAddress] = []

    originalResponses = await asyncio.gather(*tasks)

    for originalResponse in originalResponses:
        for contractAddress, addressBalance in originalResponse.items():
            response[contractAddress].append(addressBalance)

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    return response


async def getAddressPendingTransactions(address, contractAddress, config):

    try:

        pendingTask = HTTPConnector.post(
            endpoint=config.rpcEndpoint,
            path=GRAPHQL_PATH,
            json={
                "query": "query { pending { transactions { hash from { address } to { address } inputData } } }"
            }
        )

    except httpError.Error as err:
        logger.printError(f"Could not retrieve pending transactions using Graphql query. {err}")
        return []

    txs = []

    abi = utils.getFunctionABI(
        utils.getABISchema(TRANSFER_METHOD_ERC_20_ABI)
    )

    contract = Web3().eth.contract(
        address=Web3.toChecksumAddress(contractAddress),
        abi=[abi]
    )

    pendingTransactions = await pendingTask

    for tx in pendingTransactions["data"]["pending"]["transactions"]:
        if utils.addressIsInvolvedInTx(address=address, contract=contract, transaction=tx):
            txs.append(tx["hash"])

    return txs


async def getAddressConfirmedTransactions(address, contractAddress, config):

    try:
        txs = await HTTPConnector.get(
            endpoint=config.indexerEndpoint,
            path=INDEXER_TXS_PATH,
            params={
                "and": f"(and(status.eq.true,txto.eq.{contractAddress},or(txfrom.eq.{address},contract_to.like.*{address[2:]})))",
                "order": "time.desc"
            }
        )

    except httpError.Error as err:
        raise error.RpcError(
            id=id,
            message=err.message,
            code=err.code
        )

    return [tx["txhash"] for tx in txs]
