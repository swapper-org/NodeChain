#!/usr/bin/python3
import math
from decimal import Decimal
import random
import sys
from logger import logger
from rpcutils import error
from wsutils import topics
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
        id = random.randint(1, sys.maxsize)

        if len(addrTopicSplitted) <= 1:
            logger.printError(f"Topic name [{self.topicName}] not valid for Address Balance WS")
            raise error.RpcInternalServerError(id=id, message=f"Can not unsubscribe {self.topicName} to node")

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
            raise error.RpcBadRequestError(id=id, message=f"Can not unsubscribe {self.topicName} to node")


def decodeTransactionDetails(txDecoded, id, config):

    outputs = []
    for output in txDecoded["vout"]:
        if "addresses" in output["scriptPubKey"] and len(output["scriptPubKey"]["addresses"]) == 1:
            outputs.append(
                {
                    "amount": math.trunc(output["value"] * 10 * BTC_PRECISION),
                    "address": output["scriptPubKey"]["addresses"][0]
                }
            )
        else:
            outputs.append(
                {
                    "amount": math.trunc(output["value"] * 10 * BTC_PRECISION),
                    "address": None
                }
            )

    sumOutputs = sum([output["amount"] for output in outputs])

    inputs = []
    for txInput in txDecoded["vin"]:

        if "coinbase" in txInput:  # This is a coinbase transaction and thus it have one only input of 'sumOutputs'
            inputs.append(
                {
                    "amount": sumOutputs,
                    "address": None
                }
            )
            break

        transaction = apirpc.getTransactionHex(
            id=id,
            params={
                "txHash": txInput["txid"],
                "verbose": True
            },
            config=config
        )

        for txOutput in transaction["rawTransaction"]["vout"]:
            if txOutput["n"] == txInput["vout"] and "addresses" in txOutput["scriptPubKey"] and len(
                    txOutput["scriptPubKey"]["addresses"]) == 1:
                inputs.append(
                    {
                        "amount": math.trunc(txOutput["value"] * 10 * BTC_PRECISION),
                        "address": txOutput["scriptPubKey"]["addresses"][0]
                    }
                )
            elif "addresses" not in txOutput["scriptPubKey"] or len(txOutput["scriptPubKey"]["addresses"]) != 1:
                inputs.append(
                    {
                        "amount": math.trunc(txOutput["value"] * 10 * BTC_PRECISION),
                        "address": None
                    }
                )

    sumInputs = sum([txInput["amount"] for txInput in inputs])

    return {
        "fee": sumInputs - sumOutputs,
        "inputs": inputs,
        "outputs": outputs
    }


def sortUnspentOutputs(outputs):
    try:
        return outputs['txHash']
    except KeyError:
        return ''
