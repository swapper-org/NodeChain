#!/usr/bin/python3
import os
from posixpath import join
from .constants import *
from logger import logger


def getMethodSchemas(name):
    return getRequestMethodSchema(name), getResponseMethodSchema(name)


def getRequestMethodSchema(name):
    return RPC_JSON_SCHEMA_FOLDER + name + SCHEMA_CHAR_SEPARATOR + REQUEST + SCHEMA_EXTENSION


def getResponseMethodSchema(name):
    return RPC_JSON_SCHEMA_FOLDER + name + SCHEMA_CHAR_SEPARATOR + RESPONSE + SCHEMA_EXTENSION


def getWalletName():
    walletPath = "../../packages/nodechain-monero-wallet/wallet-dir"
    if not os.path.exists(walletPath):
        logger.printError(f"Path to wallet folder doesn't exist: {walletPath}")
        return

    files = [f for f in os.listdir(walletPath) if os.path.isfile(join(walletPath, f))]
    walletFile = [f for f in files if f.endswith(".keys")]

    return os.path.splitext(walletFile[0])[0]
