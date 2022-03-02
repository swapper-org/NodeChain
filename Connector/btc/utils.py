#!/usr/bin/python3
import binascii
import hashlib
import math
from decimal import Decimal
import random
import sys
from logger import logger
from rpcutils import error
from wsutils import topics
from rpcutils.rpcconnector import RPCConnector
from rpcutils.rpcsocketconnector import RPCSocketConnector
from .constants import *
from . import apirpc


def convertToSatoshi(strAmount):
    return str(int(Decimal(strAmount) * 100000000))


def convertKbToBytes(strAmount):
    return str(int(Decimal(strAmount) / 1000))


def getMethodSchemas(name):
    return getRequestMethodSchema(name), getResponseMethodSchema(name)


def getRequestMethodSchema(name):
    return RPC_JSON_SCHEMA_FOLDER + name + SCHEMA_CHAR_SEPARATOR + REQUEST + SCHEMA_EXTENSION


def getResponseMethodSchema(name):
    return RPC_JSON_SCHEMA_FOLDER + name + SCHEMA_CHAR_SEPARATOR + RESPONSE + SCHEMA_EXTENSION


def getWSMethodSchemas(name):
    return getWSRequestMethodSchema(name), getWSResponseMethodSchema(name)


def getWSRequestMethodSchema(name):
    return WS_JSON_SCHEMA_FOLDER + name + SCHEMA_CHAR_SEPARATOR + REQUEST + SCHEMA_EXTENSION


def getWSResponseMethodSchema(name):
    return WS_JSON_SCHEMA_FOLDER + name + SCHEMA_CHAR_SEPARATOR + RESPONSE + SCHEMA_EXTENSION


class AddrBalanceTopicCloseHandler:

    def __init__(self, topicName, config):
        self.topicName = topicName
        self.config = config

    def close(self):

        addrTopicSplitted = self.topicName.split(topics.TOPIC_SEPARATOR)

        if len(addrTopicSplitted) <= 1:
            logger.printError(f"Topic name [{self.topicName}] not valid for Address Balance WS")
            raise error.RpcInternalServerError(f"Can not unsubscribe {self.topicName} to node")

        id = random.randint(1, sys.maxsize)

        response = apirpc.notify(
            id,
            {
                "address": addrTopicSplitted[3],
                "callBackEndpoint": ""
            },
            self.config
        )

        if not response["success"]:
            logger.printError(f"Can not unsubscribe {self.topicName} to node")
            raise error.RpcBadRequestError(f"Can not unsubscribe {self.topicName} to node")


def decodeTransactionDetails(txDecoded, bitcoincoreRpcEndpoint):
    outputs = []
    for output in txDecoded["vout"]:
        if "addresses" in output["scriptPubKey"] and len(output["scriptPubKey"]["addresses"]) == 1:
            outputs.append(
                {"amount": math.trunc(output["value"] * 100000000), "address": output["scriptPubKey"]["addresses"][0]})
        else:
            outputs.append({"amount": math.trunc(output["value"] * 100000000), "address": None})

    sumOutputs = 0
    for output in outputs:
        sumOutputs += output["amount"]

    inputs = []
    for txInput in txDecoded["vin"]:

        if "coinbase" in txInput:  # This is a coinbase transaction and thus it have one only input of 'sumOutputs'
            inputs.append({"amount": sumOutputs, "address": None})
            break

        transaction = RPCConnector.request(
            endpoint=bitcoincoreRpcEndpoint,
            id=0,
            method="getrawtransaction",
            params=[
                txInput["txid"],
                True
            ]
        )

        for txOutput in transaction["vout"]:
            if txOutput["n"] == txInput["vout"] and "addresses" in txOutput["scriptPubKey"] and len(
                    txOutput["scriptPubKey"]["addresses"]) == 1:
                inputs.append({"amount": math.trunc(txOutput["value"] * 100000000),
                               "address": txOutput["scriptPubKey"]["addresses"][0]})
            elif "addresses" not in txOutput["scriptPubKey"] or len(txOutput["scriptPubKey"]["addresses"]) != 1:
                inputs.append({"amount": math.trunc(txOutput["value"] * 100000000), "address": None})

    sumInputs = 0
    for txInput in inputs:
        sumInputs += txInput["amount"]

    fee = sumInputs - sumOutputs

    transactionsDetails = {"fee": fee, "inputs": inputs, "outputs": outputs}

    return transactionsDetails


def sortUnspentOutputs(outputs):
    try:
        return outputs['txHash']
    except KeyError:
        return ''
