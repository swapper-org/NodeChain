#!/usr/bin/python
from httputils import httputils
from httputils.httpmethod import RouteTableDef as HttpRouteTableDef
from .constants import *
from rpcutils import error
from rpcutils.rpcmethod import RouteTableDef as RpcRouteTableDef
from rpcutils.rpcconnector import RPCConnector
from . import utils
from logger import logger


@RpcRouteTableDef.rpc(currency=COIN_SYMBOL)
@HttpRouteTableDef.get(currency=COIN_SYMBOL)
async def syncing(id, params, config):

    logger.printInfo(f"Executing RPC method syncing with id {id} and params {params}")

    requestSchema, responseSchema = utils.getMethodSchemas(SYNCING)

    err = httputils.validateJSONSchema(params, requestSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    blockchainInfo = await RPCConnector.request(
        endpoint=config.rpcEndpoint,
        id=id,
        method=GET_INFO,
        params=None
    )

    if blockchainInfo is None:
        logger.printWarning("Could not get blockchain info from node")
        raise error.RpcBadRequestError(
            id=id,
            message="Could not get blockchain info from node"
        )

    if not blockchainInfo["synchronized"]:
        syncInfo = await RPCConnector.request(
            endpoint=config.rpcEndpoint,
            id=id,
            method=GET_SYNC_INFO,
            params=None
        )

        if syncInfo is None:
            logger.printWarning("Could not get syncing info from node")
            raise error.RpcBadRequestError(
                id=id,
                message="Could not get syncing info from node"
            )

        response = {
            "syncing": True,
            "syncPercentage": f'{str(syncInfo["height"] / syncInfo["target_height"] * 100)}%',
            "currentBlock": str(syncInfo["height"]),
            "latestBlock": str(syncInfo["target_height"])
        }
    else:
        response = {"syncing": False}

    err = httputils.validateJSONSchema(response, responseSchema)
    if err is not None:
        raise error.RpcBadRequestError(
            id=id,
            message=err.message
        )

    return response
