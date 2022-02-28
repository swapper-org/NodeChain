#!/usr/bin/python3
import binascii
import hashlib
import math
from decimal import Decimal
import random
import sys
from logger import logger
from rpcutils import error as rpcerrorhandler
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


def closeAddrBalanceTopic(topicName):

    addrTopicSplitted = topicName.split(topics.TOPIC_SEPARATOR)

    if len(addrTopicSplitted) <= 1:
        logger.printError(f"Topic name [{topicName}] not valid for Address Balance WS")
        raise rpcerrorhandler.RpcInternalServerError(f"Can not unsubscribe {topicName} to node")

    id = random.randint(1, sys.maxsize)

    response = apirpc.notify(
        id,
        {
            "success": addrTopicSplitted[1],
            "callBackEndpoint": ""
        }
    )

    if not response["success"]:
        logger.printError(f"Can not unsubscribe {topicName} to node")
        raise rpcerrorhandler.BadRequestError(f"Can not unsubscribe {topicName} to node")


def getWorkaroundScriptHash(txDecoded):
    script = txDecoded["vout"][0]["scriptPubKey"]["hex"]
    scriptUnex = binascii.unhexlify(script)
    hash = hashlib.sha256(scriptUnex).digest()[::-1].hex()
    return hash


def getTransactionTransfers(txDecoded, bitcoincoreRpcEndpoint, electrumxHost, electrumxPort):
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

        if "coinbase" in txInput:  # This is a coinbase transaction and thus it have one only input of 'sumOutputs' amount
            inputs.append({"amount": sumOutputs, "address": None})
            break

        txInRaw = RPCSocketConnector.sendRequest(electrumxHost, electrumxPort, 0, "blockchain.transaction.get",
                                         [txInput["txid"]])
        txInDecoded = RPCConnector.request(bitcoincoreRpcEndpoint, "decoderawtransaction",
                                           [txInRaw])

        for txOutput in txInDecoded["vout"]:
            if txOutput["n"] == txInput["vout"] and "addresses" in txOutput["scriptPubKey"] and len(
                    txOutput["scriptPubKey"]["addresses"]) == 1:
                inputs.append({"amount": math.trunc(txOutput["value"] * 100000000),
                               "address": txOutput["scriptPubKey"]["addresses"][0]})
            elif len(txOutput["scriptPubKey"]["addresses"]) != 1:
                inputs.append({"amount": math.trunc(txOutput["value"] * 100000000), "address": None})

    sumInputs = 0
    for txInput in inputs:
        sumInputs += txInput["amount"]

    sumOutputs = 0
    for txOutput in outputs:
        sumOutputs += txOutput["amount"]

    fee = sumInputs - sumOutputs

    transfers = {}
    for inputTx in inputs:
        inputTotalProvide = inputTx["amount"] - (fee / len(inputs))
        for txOutput in outputs:
            outputPercentage = txOutput["amount"] / sumOutputs

            if (inputTx["address"], txOutput["address"]) in transfers:
                transfers[(inputTx["address"], txOutput["address"])] = transfers[(
                    inputTx["address"], txOutput["address"])] + (inputTotalProvide * outputPercentage)
            else:
                transfers[(inputTx["address"], txOutput["address"])] = inputTotalProvide * outputPercentage

    transfersResult = []
    for key in transfers.keys():
        transfersResult.append({"from": key[0], "to": key[1], "amount": transfers[key]})
    return transfersResult


def sortUnspentOutputs(outputs):
    try:
        return outputs['txHash']
    except KeyError:
        return ''
