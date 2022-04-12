#!/usr/bin/python
from web3 import Web3
from rpcutils import rpcmethod, error
from httputils import httpmethod
from eth import apirpc as ethapirpc, utils as ethutils
from eth.constants import COIN_SYMBOL
from httputils import httputils
from logger import logger
from .constants import *
from . import utils


@rpcmethod.rpcMethod(coin=COIN_SYMBOL, standard=ERC20_STANDARD_SYMBOL)
@httpmethod.httpMethod(coin=COIN_SYMBOL, standard=ERC20_STANDARD_SYMBOL)
def getAddressBalance(id, params, config):

    logger.printInfo(f"Executing RPC method getAddressBalance with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(GET_ADDRESS_BALANCE)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    abi = utils.getFunctionABI(
        utils.getABIFilename(BALANCE_OF_METHOD_ECR20_ABI)
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

        result = ethapirpc.call(
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


@rpcmethod.rpcMethod(coin=COIN_SYMBOL, standard=ERC20_STANDARD_SYMBOL)
@httpmethod.httpMethod(coin=COIN_SYMBOL, standard=ERC20_STANDARD_SYMBOL)
def getAddressesBalance(id, params, config):

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

    for address in params["addresses"]:

        addressBalances = getAddressBalance(
            id=id,
            params={
                "address": address,
                "contractAddresses": params["contractAddresses"]
            },
            config=config
        )

        for contractAddress, addressBalance in addressBalances.items():
            response[contractAddress].append(addressBalance)

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    return response
