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
