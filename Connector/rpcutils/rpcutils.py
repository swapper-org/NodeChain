import json
import jsonschema
from . import error
from .constants import *
from logger import logger

RPCMethods = {}


def rpcMethod(f):
    logger.printInfo(f"Registering new RPC method: {f.__name__}")
    RPCMethods[f.__name__] = f
    return f


def parseJsonRpcRequest(request):

    if METHOD not in request or PARAMS not in request or JSON_RPC not in request or ID not in request:
        logger.printError("JSON request is malformed")
        raise error.RpcBadRequestError(
            id=request[ID] if ID in request else 0,
            message="JSON request is malformed")

    if not isinstance(request[METHOD], str):
        logger.printError(f"{METHOD} must be string")
        raise error.RpcBadRequestError(
            id=request[ID],
            message=f"{METHOD} must be string"
        )

    if not isinstance(request[PARAMS], dict):
        logger.printError(f"{PARAMS} must be dictionary")
        raise error.RpcBadRequestError(
            id=request[ID],
            message=f"{PARAMS} must be dictionary"
        )

    if request[JSON_RPC] != JSON_RPC_VERSION:
        logger.printError(f"This version of JSON RPC is not supported. Supported version: {JSON_RPC_VERSION}")
        raise error.RpcBadRequestError(
            id=request[ID],
            message=f"This version of JSON RPC is not supported. Supported version: {JSON_RPC_VERSION}"
        )

    if not isinstance(request[ID], int):
        logger.printError(f"{ID} must be integer")
        raise error.RpcBadRequestError(
            id=request[ID],
            message="{ID} must be integer"
        )

    return {
        METHOD: request[METHOD],
        PARAMS: request[PARAMS],
        ID: request[ID]
    }


def validateJSONRPCSchema(params, jsonSchemaFile):

    logger.printInfo(f"Validating JSON RPC Schema with {jsonSchemaFile}")

    try:
        with open(jsonSchemaFile) as file:
            schema = json.load(file)
            try:
                jsonschema.validate(instance=params, schema=schema)
            except jsonschema.exceptions.ValidationError as err:
                logger.printError(f"Error validation params with schema: {err}")
                return err
    except FileNotFoundError as err:
        logger.printError(f"Schema {jsonSchemaFile} not found: {err}")
        raise error.InternalServerError(f"Schema {jsonSchemaFile} not found: {err}")

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
