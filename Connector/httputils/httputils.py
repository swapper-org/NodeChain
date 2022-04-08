#!/usr/bin/python3
import json
from logger import logger
from . import error
import jsonschema


def parseJSONRequest(request):

    try:
        return json.loads(request)
    except Exception as e:
        logger.printError(f"Payload is not JSON message: {e}")
        raise error.BadRequestError(f"Payload is not JSON message: {e}")


def validateJSONSchema(payload, schemaFile):

    logger.printInfo(f"Validating JSON schema with {schemaFile}")

    try:
        with open(schemaFile) as file:
            schema = json.load(file)
            try:
                jsonschema.validate(instance=payload, schema=schema)
            except jsonschema.exceptions.ValidationError as err:
                logger.printError(f"Error validation payload with schema: {err}")
                return err
    except FileNotFoundError as err:
        logger.printError(f"Schema {schemaFile} not found: {err}")
        raise error.InternalServerError(f"Schema {schemaFile} not found: {err}")

    return None


def isGetMethod(method):
    return method == "GET"


def isPostMethod(method):
    return method == "POST"
