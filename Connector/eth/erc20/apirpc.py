#!/usr/bin/python
import asyncio
from web3 import Web3
from rpcutils import error
from rpcutils.rpcmethod import RouteTableDef as RpcRouteTableDef
from httputils.httpmethod import RouteTableDef as HttpRouteTableDef
from eth import apirpc as ethapirpc, utils as ethutils
from eth.constants import COIN_SYMBOL
from httputils import httputils
from logger import logger
from .constants import *
from . import utils


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

    response = {}
    for contractAddress in params["contractAddresses"]:
        response[contractAddress] = []

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

    transaction = ethapirpc.getTransaction(
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
