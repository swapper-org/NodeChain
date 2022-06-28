#!/usr/bin/python3
import hashlib
import base58
import bech32
import binascii
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


async def decodeTransactionDetails(txDecoded, id, config):

    outputs = []
    for output in txDecoded["vout"]:
        if "addresses" in output["scriptPubKey"] and len(output["scriptPubKey"]["addresses"]) == 1:
            outputs.append(
                {
                    "amount": math.trunc(output["value"] * math.pow(10, BTC_PRECISION)),
                    "address": output["scriptPubKey"]["addresses"][0]
                }
            )
        else:
            outputs.append(
                {
                    "amount": math.trunc(output["value"] * math.pow(10, BTC_PRECISION)),
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

        transaction = await apirpc.getTransactionHex(
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
                        "amount": math.trunc(txOutput["value"] * math.pow(10, BTC_PRECISION)),
                        "address": txOutput["scriptPubKey"]["addresses"][0]
                    }
                )
            elif "addresses" not in txOutput["scriptPubKey"] or len(txOutput["scriptPubKey"]["addresses"]) != 1:
                inputs.append(
                    {
                        "amount": math.trunc(txOutput["value"] * math.pow(10, BTC_PRECISION)),
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


def isHexNumber(number: str):
    return any(number.startswith(prefix) for prefix in ["0x", "0X"])


class ScriptHash:

    @staticmethod
    def script_to_scripthash(script):
        return hashlib.sha256(script).digest()[::-1].hex()

    @staticmethod
    def bitstring_to_bytes(s):
        return int(s, 2).to_bytes((len(s) + 7) // 8, byteorder='big')

    @staticmethod
    def demod(intarray):
        result = []
        for x in intarray:
            result.append(format(x, "05b"))
        return ScriptHash.bitstring_to_bytes(''.join(result))[1:]

    @staticmethod
    def bech32_to_script(address):
        bech32_decoded = bech32.bech32_decode(address)
        if not bech32_decoded[1]:
            raise ValueError
        hash160hex = ScriptHash.demod(bech32_decoded[1]).hex()
        return binascii.unhexlify("0014" + hash160hex)

    @staticmethod
    def p2pkh_address_to_script(address):
        hash160hex = base58.b58decode(address)[1:21].hex()
        return binascii.unhexlify("76a914" + hash160hex + "88ac")

    @staticmethod
    def p2sh_address_to_script(address):
        hash160hex = base58.b58decode(address)[1:21].hex()
        return binascii.unhexlify("a914" + hash160hex + "87")

    @staticmethod
    def addressToScriptHash(address):
        if address.startswith(("1", "m", "n")):
            return ScriptHash.script_to_scripthash(ScriptHash.p2pkh_address_to_script(address))

        if address.startswith(("2", "3")):
            return ScriptHash.script_to_scripthash(ScriptHash.p2sh_address_to_script(address))

        if address.startswith(("bc1", "tb1", "bcrt1")):
            return ScriptHash.script_to_scripthash(ScriptHash.bech32_to_script(address))

        raise ValueError
