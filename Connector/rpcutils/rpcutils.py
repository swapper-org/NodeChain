#!/usr/bin/python3
import json
import jsonschema
from . import error
from httputils import error as httpError
from .constants import *
from logger.logger import Logger

RPCMethods = {}


def rpcMethod(f):
    Logger.printDebug(f"Registering new RPC method: {f.__name__}")
    RPCMethods[f.__name__] = f
    return f


def parseJsonRpcRequest(request):

    if METHOD not in request or PARAMS not in request or JSON_RPC not in request or ID not in request:
        Logger.printError("JSON request is malformed")
        raise error.RpcBadRequestError(
            id=request[ID] if ID in request else 0,
            message="JSON request no following RPC format"
        )

    if request[JSON_RPC] != JSON_RPC_VERSION:
        Logger.printError(f"This version of JSON RPC is not supported. Supported version: {JSON_RPC_VERSION}")
        raise error.RpcBadRequestError(
            id=request[ID],
            message="JSON request no following RPC format"
        )

    if not isinstance(request[ID], int):
        Logger.printError(f"{ID} must be integer")
        raise error.RpcBadRequestError(
            id=0,
            message="JSON request no following RPC format"
        )

    if not isinstance(request[METHOD], str):
        Logger.printError(f"{METHOD} must be string")
        raise error.RpcBadRequestError(
            id=request[ID],
            message="JSON request no following RPC format"
        )

    if not isinstance(request[PARAMS], dict):
        Logger.printError(f"{PARAMS} must be dictionary")
        raise error.RpcBadRequestError(
            id=request[ID],
            message="JSON request no following RPC format"
        )

    return {
        METHOD: request[METHOD],
        PARAMS: request[PARAMS],
        ID: request[ID]
    }


def validateJSONRPCSchema(params, jsonSchemaFile):

    Logger.printDebug(f"Validating JSON RPC Schema with {jsonSchemaFile}")

    try:
        with open(jsonSchemaFile) as file:
            schema = json.load(file)
            try:
                jsonschema.validate(instance=params, schema=schema)
            except jsonschema.exceptions.ValidationError as err:
                Logger.printError(f"Error validation params with schema: {err}")
                return err
    except FileNotFoundError as err:
        Logger.printError(f"Schema {jsonSchemaFile} not found: {err}")
        raise httpError.InternalServerError()

    return None


def generateRPCResponse(id, response):

    if CODE in response and MESSAGE in response:
        return generateRPCErrorResponse(id, response)
    return generateRPCResultResponse(id, response)


def generateRPCResultResponse(id, params):

    return {
        ID: id,
        JSON_RPC: JSON_RPC_VERSION,
        RESULT: params
    }


def generateRPCErrorResponse(id, err):

    return {
        ID: id,
        JSON_RPC: JSON_RPC_VERSION,
        ERROR: {
            CODE: err[CODE],
            MESSAGE: err[MESSAGE]
        }
    }


def isRPCErrorResponse(response):
    return CODE in response or MESSAGE in response


def isRpcEnpointPath(method):
    return method == RPC_ENDPOINT_PATH
