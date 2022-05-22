#!/usr/bin/python3
import json
from logger import logger
from . import error
import jsonschema
from utils import utils


def parseJSONRequest(request):

    try:
        return json.loads(request)
    except Exception as e:
        logger.printError(f"Payload is not JSON message: {e}")
        raise error.BadRequestError(f"Payload is not JSON message: {e}")


def validateJSONSchema(payload, schemaFile):

    logger.printInfo(f"Validating JSON schema with {schemaFile}")

    schema = utils.openSchemaFile(schemaFile=schemaFile)

    try:
        jsonschema.validate(instance=payload, schema=schema)
        return None
    except jsonschema.exceptions.ValidationError as err:
        logger.printError(f"Error validation payload with schema: {err}")
        return err


def isGetMethod(method):
    return method == "GET"


def isPostMethod(method):
    return method == "POST"
