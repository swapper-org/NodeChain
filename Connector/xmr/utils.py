#!/usr/bin/python3
from .constants import *


def getMethodSchemas(name):
    return getRequestMethodSchema(name), getResponseMethodSchema(name)


def getRequestMethodSchema(name):
    return f"{RPC_JSON_SCHEMA_FOLDER}{name}{SCHEMA_CHAR_SEPARATOR}{REQUEST}{SCHEMA_EXTENSION}"


def getResponseMethodSchema(name):
    return f"{RPC_JSON_SCHEMA_FOLDER}{name}{SCHEMA_CHAR_SEPARATOR}{RESPONSE}{SCHEMA_EXTENSION}"
