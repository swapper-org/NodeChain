#!/usr/bin/python3
import json
from logger.logger import Logger
from . import error
import jsonschema
from utils import utils


def parseJSONRequest(request):

    try:
        return json.loads(request)
    except Exception as e:
        Logger.printError(f"Payload is not JSON message: {e}")
        raise error.BadRequestError("Payload is not JSON message")


def validateJSONSchema(payload, schemaFile):

    Logger.printDebug(f"Validating JSON schema with {schemaFile}")

    schema = utils.openSchemaFile(schemaFile=schemaFile)

    try:
        jsonschema.validate(instance=payload, schema=schema)
        return None
    except jsonschema.exceptions.ValidationError as err:
        Logger.printError(f"Error validation payload with schema: {err}")
        return err


def isGetMethod(method):
    return method == "GET"


def isPostMethod(method):
    return method == "POST"
