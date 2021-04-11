import json
import jsonschema
from . import errorhandler
from .constants import *

RPCMethods = {}

def rpcMethod (f):
    RPCMethods[f.__name__] = f
    return f

 
def parseRpcRequest(request):

    try:
        parsedRequest = json.loads(request)
    except Exception as e:
        raise errorhandler.BadRequestError("Payload is not JSON message: " + str(e))

    if METHOD not in parsedRequest or PARAMS not in parsedRequest or JSON_RPC not in parsedRequest or ID not in parsedRequest:
        raise errorhandler.BadRequestError("JSON request is malformed")

    if not isinstance(parsedRequest[METHOD], str):
        raise errorhandler.BadRequestError(METHOD + " must be a string")

    if not isinstance(parsedRequest[PARAMS], dict):
        raise errorhandler.BadRequestError(PARAMS + " must be an dictionary")

    if parsedRequest[JSON_RPC] != JSON_RPC_VERSION:
        raise errorhandler.BadRequestError("This version of JSON RPC is not supported. Supported version: " + JSON_RPC_VERSION)

    if not isinstance(parsedRequest[ID], int):
        raise errorhandler.BadRequestError(ID + " must be integer")

    return {
        METHOD: parsedRequest[METHOD],
        PARAMS: parsedRequest[PARAMS],
        ID: parsedRequest[ID]
    }


def validateJSONRPCSchema(params, jsonSchemaFile):
    
    with open(jsonSchemaFile) as file:
        schema = json.load(file)
        try:
            jsonschema.validate(instance=params, schema=schema)
        except jsonschema.exceptions.ValidationError as err:
            return err

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

def unifyResponse(response):

    parsedResponse = {}

    if isinstance(response, list):
        return unifyArray(response)

    for key, value in response.items():

        parsedKey = stringToCamelCase(key)
        
        if isinstance(value, dict):
            parsedResponse[parsedKey] = unifyResponse(value)
        elif isinstance(value, list):
            parsedResponse[parsedKey] = unifyArray(value)
        elif isinstance(value, bool):
            parsedResponse[parsedKey] = value
        elif isinstance(value, (int, float)):
            parsedResponse[parsedKey] = str(value)
        else:
            parsedResponse[parsedKey] = value

    return parsedResponse


def unifyArray(array):

    parsedArray = []

    for element in array:
        if isinstance(element, dict):
            parsedArray.append(unifyResponse(element))
        elif isinstance(element, list):
            parsedArray.append(unifyArray(element))
        elif isinstance(element, bool):
            parsedArray.append(element)
        elif isinstance(element, (int, float)):
            parsedArray.append(str(element))
        else:
            parsedArray.append(element)

    return parsedArray

def stringToCamelCase(string):

    translations = {
        "txinwitness": "txInWitness",
        "previousblockhash": "previousBlockHash",
        "nextblockhash": "nextBlockHash",
        "strippedsize": "strippedSize",
        "merkleroot": "merkleRoot"
    }

    if string in translations:
        return translations[string]
    else:
        init, *temp = string.split("_")
        return ''.join([init, *map(str.title, temp)]) 
