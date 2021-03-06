#!/usr/bin/python
from .constants import *
from os import environ


def getAdminMethodSchemas(name):
    return getAdminRequestMethodSchema(name), getAdminResponseMethodSchema(name)


def getAdminRequestMethodSchema(name):
    return f"{ADMIN_SCHEMA_FOLDER}{name}{ADMIN_SCHEMA_CHAR_SEPARATOR}request.json"


def getAdminResponseMethodSchema(name):
    return f"{ADMIN_SCHEMA_FOLDER}{name}{ADMIN_SCHEMA_CHAR_SEPARATOR}response.json"


def getApiKey():
    return environ.get("API_KEY", None)
