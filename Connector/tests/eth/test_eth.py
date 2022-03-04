#!/usr/bin/python3
import json
import pytest
import time
from web3 import Web3
from eth.config import Config
from eth.constants import *
from eth.websockets import WebSocket
from eth import utils
from logger import logger
from httputils.httpmethod import postHttpMethods
from rpcutils.rpcconnector import RPCConnector
from wsutils.wsmethod import wsMethods
from wsutils.subscribers import ListenerSubscriber
from wsutils import websocket


networkName = "regtest"
config = Config(
    coin=COIN_SYMBOL,
    networkName=networkName
)
config.loadConfig(
    config={
        "host": "localhost"
    }
)

WebSocket(
    coin=COIN_SYMBOL,
    config=config
)

websocket.startWebSockets(COIN_SYMBOL, networkName)


address1 = "0x625ACaEdeF812d2842eFd2Fb0294682A868455bd"
privateKey1 = "0x6fa76995e9a39e852f893e8347c662453a5d517846d150bdf3ddf7601c4bc74c"

address2 = "0x93261B4021dbd6200Df9B36B151f4ECF34889e94"

sub = ListenerSubscriber()
newBlocksSub = ListenerSubscriber()


def makeTransaction(address1=address1, address2=address2, value=1, gas=2000000):

    web3 = Web3(Web3.HTTPProvider(config.rpcEndpoint))

    nonce = web3.eth.getTransactionCount(address1)

    tx = {
        "nonce": nonce,
        "to": address2,
        "value": web3.toWei(value, 'ether'),
        "gas": gas,
        "gasPrice": web3.toWei('50', 'gwei')
    }

    signedTx = web3.eth.account.sign_transaction(tx, privateKey1)
    txHash = web3.eth.sendRawTransaction(signedTx.rawTransaction)

    return signedTx.rawTransaction, txHash


def makeEtherumgoRequest(method, params):

    try:
        return RPCConnector.request(config.rpcEndpoint, 1, method, params)
    except Exception as err:
        logger.printError(f"Can not make request to {config.rpcEndpoint}. {err}")
        assert False


def testGetAddressBalance():

    if "getAddressBalance" not in postHttpMethods[COIN_SYMBOL]:
        logger.printError("Method getAddressBalance not loaded")
        assert False

    expectedLatest = makeEtherumgoRequest(
        GET_BALANCE_METHOD,
        [address1, "latest"]
    )

    expectedPending = makeEtherumgoRequest(
        GET_BALANCE_METHOD,
        [address1, "pending"]
    )

    got = postHttpMethods[COIN_SYMBOL]["getAddressBalance"]({"address": address1}, config)

    assert got["balance"]["confirmed"] == str(int(expectedPending, 16)) and got["balance"]["unconfirmed"] == str(int(expectedPending, 16) - int(expectedLatest, 16)) and address1 == got["address"]


def testGetAddressesBalance():

    if "getAddressesBalance" not in postHttpMethods[COIN_SYMBOL]:
        logger.printError("Method getAddressBalance not loaded")
        assert False

    addresses = [address1, address2]

    got = postHttpMethods[COIN_SYMBOL]["getAddressesBalance"]({"addresses": addresses}, config)

    for address in addresses:

        expectedLatest = makeEtherumgoRequest(
            GET_BALANCE_METHOD,
            [address, "latest"]
        )
        expectedPending = makeEtherumgoRequest(
            GET_BALANCE_METHOD,
            [address, "pending"]
        )

        found = False
        for gotBalance in got:

            if gotBalance["address"] == address:
                found = True
                if not (gotBalance["balance"]["confirmed"] == str(int(expectedPending, 16)) and gotBalance["balance"]["unconfirmed"] == str(int(expectedPending, 16) - int(expectedLatest, 16))):
                    logger.printError(f"Error validating {address}")
                    assert False
        if not found:
            logger.printError(f"Can not find balance for {address}")
            assert False

    assert True


def testGetHeight():

    if "getHeight" not in postHttpMethods[COIN_SYMBOL]:
        logger.printError("Method getHeight not loaded")
        assert False

    got = postHttpMethods[COIN_SYMBOL]["getHeight"]({}, config)

    expected = makeEtherumgoRequest(
        GET_BLOCK_BY_NUMBER_METHOD,
        ["latest", True]
    )

    assert str(int(expected["number"], 16)) == got["latestBlockIndex"] and expected["hash"] == got["latestBlockHash"]


"""
def testGetTransaction():

    if "getTransaction" not in postHttpMethods[COIN_SYMBOL]:
        logger.printError("Method getTransaction not loaded")
        assert False

    _, txHash = makeTransaction()

    got = postHttpMethods[COIN_SYMBOL]["getTransaction"](
        {
            "txHash": txHash.hex()
        },
        config
    )

    expected = makeEtherumgoRequest(GET_TRANSACTION_BY_HASH_METHOD, [txHash.hex()])

    assert json.dumps(got["transaction"]["data"], sort_keys=True) == json.dumps(expected, sort_keys=True)
    assert got["transaction"]["blockHash"] == expected["blockHash"]
    assert got["transaction"]["fee"] == str(utils.toWei(expected["gas"]) * utils.toWei(expected["gasPrice"]))

    for transfer in got["transaction"]["transfers"]:
        assert transfer["to"] == expected["to"]
        assert transfer["from"] == expected["from"]
        assert transfer["amount"] == str(utils.toWei(expected["value"]))
        assert transfer["fee"] == str(utils.toWei(expected["gas"]) * utils.toWei(expected["gasPrice"]))
"""


def testEstimateGas():

    if "estimateGas" not in postHttpMethods[COIN_SYMBOL]:
        logger.printError("Method estimateGas not loaded")
        assert False

    web3 = Web3(Web3.HTTPProvider(config.rpcEndpoint))

    nonce = web3.eth.getTransactionCount(address1)

    tx = {
        "nonce": nonce,
        "to": address2,
        "value": str(web3.toWei(1, 'ether')),
        "gas": "2000000",
        "gasPrice": str(web3.toWei('50', 'gwei'))
    }

    got = postHttpMethods[COIN_SYMBOL]["estimateGas"](
        {
            "tx": tx
        },
        config
    )
    expected = makeEtherumgoRequest(ESTIMATE_GAS_METHOD, [tx])

    assert got["estimatedGas"] == str(int(expected, 16))


def testGetGasPrice():

    if "getGasPrice" not in postHttpMethods[COIN_SYMBOL]:
        logger.printError("Method getGasPrice not loaded")
        assert False

    got = postHttpMethods[COIN_SYMBOL]["getGasPrice"](
        {},
        config
    )
    expected = makeEtherumgoRequest(
        GET_GAS_PRICE_METHOD,
        None
    )

    assert str(int(expected, 16)) == got["gasPrice"]


def testGetTransactionReceipt():

    if "getTransactionReceipt" not in postHttpMethods[COIN_SYMBOL]:
        logger.printError("Method getTransactionReceipt not loaded")
        assert False

    _, txHash = makeTransaction()
    got = postHttpMethods[COIN_SYMBOL]["getTransactionReceipt"]({"txHash": txHash.hex()}, config)
    expected = makeEtherumgoRequest(GET_TRANSACTION_RECEIPT_METHOD, [txHash.hex()])

    for key in expected:
        if key not in got:
            logger.printError(f"{key} not found in Connector response")
            assert False
        if got[key] != expected[key]:
            logger.printError("Transaction receipt data not correct")
            assert False

    assert True


def testGetAddressTransactionCount():

    if "getAddressTransactionCount" not in postHttpMethods[COIN_SYMBOL]:
        logger.printError("Method getAddressTransactionCount not loaded")
        assert False

    got = postHttpMethods[COIN_SYMBOL]["getAddressTransactionCount"](
        {
            "address": address1,
            "pending": True
        },
        config
    )

    expected = makeEtherumgoRequest(GET_TRANSACTION_COUNT_METHOD, [address1, "pending"])

    assert json.dumps(got, sort_keys=True) == json.dumps(
        {
            "address": address1,
            "transactionCount": str(int(expected, 16))
        }, sort_keys=True)


def testGetAddressesTransactionCount():

    if "getAddressesTransactionCount" not in postHttpMethods[COIN_SYMBOL]:
        logger.printError("Method getAddressesTransactionCount not loaded")
        assert False

    addresses = {
        "addresses": [
            {
                "address": address1,
                "pending": True
            },
            {
                "address": address2,
                "pending": False
            }
        ]
    }

    got = postHttpMethods[COIN_SYMBOL]["getAddressesTransactionCount"](addresses, config)

    for index, address in enumerate(addresses["addresses"]):

        expected = makeEtherumgoRequest(GET_TRANSACTION_COUNT_METHOD,
                                        [
                                            address["address"],
                                            "pending" if address["pending"] else "latest"
                                        ])

        assert json.dumps(got[index], sort_keys=True) == json.dumps(
            {
                "address": address["address"],
                "transactionCount": str(int(expected, 16))
            }, sort_keys=True)


def testGetBlock():

    if "getBlockByNumber" not in postHttpMethods[COIN_SYMBOL]:
        logger.printError("Method getBlockByNumber not loaded")
        assert False

    if "getBlockByHash" not in postHttpMethods[COIN_SYMBOL]:
        logger.printError("Method getBlockByHash not loaded")
        assert False

    expected = makeEtherumgoRequest(GET_BLOCK_BY_NUMBER_METHOD, ["0x1", True])

    gotBlockByNumber = postHttpMethods[COIN_SYMBOL]["getBlockByNumber"]({"blockNumber": "1"}, config)

    gotBlockByHash = postHttpMethods[COIN_SYMBOL]["getBlockByHash"]({"blockHash": expected["hash"]}, config)

    if not json.dumps(expected["transactions"], sort_keys=True) == json.dumps(gotBlockByNumber["transactions"], sort_keys=True):
        logger.printError("getBlockByNumber failed")
        assert False

    if not json.dumps(expected["transactions"], sort_keys=True) == json.dumps(gotBlockByHash["transactions"], sort_keys=True):
        logger.printError("getBlockByHash failed")
        assert False

    assert True


def testBroadCastTransaction():

    if "broadcastTransaction" not in postHttpMethods[COIN_SYMBOL]:
        logger.printError("Method broadcastTransaction not loaded")
        assert False

    if "getTransaction" not in postHttpMethods[COIN_SYMBOL]:
        logger.printError("Method getTransaction not loaded")
        assert False

    web3 = Web3(Web3.HTTPProvider(config.rpcEndpoint))

    nonce = web3.eth.getTransactionCount(address1)

    tx = {
        "nonce": nonce,
        "to": address2,
        "value": web3.toWei(1, 'ether'),
        "gas": 2000000,
        "gasPrice": web3.toWei('50', 'gwei')
    }

    signedTx = web3.eth.account.sign_transaction(tx, privateKey1)

    got = postHttpMethods[COIN_SYMBOL]["broadcastTransaction"]({"rawTransaction": signedTx.rawTransaction.hex()}, config)

    expected = makeEtherumgoRequest(GET_TRANSACTION_BY_HASH_METHOD, [got["broadcasted"]])

    assert got["broadcasted"] == expected["hash"]


def testSubscribeAddressBalance():

    if "subscribeToAddressBalance" not in wsMethods[COIN_SYMBOL]:
        logger.printError("Method subscribeToAddressBalance not loaded")
        assert False

    got = wsMethods[COIN_SYMBOL]["subscribeToAddressBalance"](
        sub,
        {
            "id": 0,
            "params":
            {
                "address": address1
            }
        },
        config
    )

    if not got["subscribed"]:
        logger.printError(f"Error in subscribe to address balance. Expected: True Got: {got['subscribed']}")
        assert False

    got = wsMethods[COIN_SYMBOL]["subscribeToAddressBalance"](
        sub,
        {
            "id": 0,
            "params": {
                "address": address1

            }
        },
        config
    )

    if got["subscribed"]:
        logger.printError(f"Error in subscribe to address balance. Expected: False Got: {got['subscribed']}")
        assert False

    assert True


def testAdressBalanceWS():

    attemps = 3
    numAttemps = 0
    makeTransaction(address1=address1, address2=address2)

    while not sub.messageReceived and numAttemps < attemps:
        numAttemps += 1
        logger.printWarning(f"Subscriber {sub.subscriberID} did not receive message at {numAttemps} attemp")
        time.sleep(1)

    assert sub.messageReceived


def testUnsubscribeFromAddressBalance():

    if "unsubscribeFromAddressBalance" not in wsMethods[COIN_SYMBOL]:
        logger.printError("Method unsubscribeFromAddressBalance not loaded")
        assert False

    got = wsMethods[COIN_SYMBOL]["unsubscribeFromAddressBalance"](
        sub,
        {
            "id": 0,
            "params": {
                "address": address1
            }
        },
        config
    )

    if not got["unsubscribed"]:
        logger.printError(f"Error in unsubscribe from address balance. Expected: True Got: {got['unsubscribed']}")
        assert False

    got = wsMethods[COIN_SYMBOL]["unsubscribeFromAddressBalance"](
        sub,
        {
            "id": 0,
            "params": {
                "address": address1
            }
        },
        config
    )

    if got["unsubscribed"]:
        logger.printError(f"Error in unsubscribe from address balance. Expected: False Got: {got['unsubscribed']}")
        assert False

    assert True


def testSubscribeToNewBlocks():

    if "subscribeToNewBlocks" not in wsMethods[COIN_SYMBOL]:
        logger.printError("Method subscribeToNewBlocks not loaded")
        assert False

    got = wsMethods[COIN_SYMBOL]["subscribeToNewBlocks"](
        newBlocksSub,
        {
            "id": 0,
            "params": {}
        },
        config
    )

    if not got["subscribed"]:
        logger.printError(f"Error in subscribe to new blocks. Expected: True Got: {got['subscribed']}")
        assert False

    got = wsMethods[COIN_SYMBOL]["subscribeToNewBlocks"](
        newBlocksSub,
        {
            "id": 0,
            "params": {}
        },
        config
    )

    if got["subscribed"]:
        logger.printError(f"Error in subscribe to new blocks. Expected: False Got: {got['subscribed']}")
        assert False

    assert True


def testNewBlocksWS():

    attemps = 3
    numAttemps = 0
    makeTransaction(address1=address1, address2=address2)

    while not newBlocksSub.messageReceived and numAttemps < attemps:
        numAttemps += 1
        logger.printWarning(f"Subscriber {newBlocksSub.subscriberID} did not receive message at {numAttemps} attemp")
        time.sleep(1)

    assert newBlocksSub.messageReceived


def testUnsubscribeFromNewBlocks():

    if "unsubscribeFromNewBlocks" not in wsMethods[COIN_SYMBOL]:
        logger.printError("Method unsubscribeFromNewBlocks not loaded")
        assert False

    got = wsMethods[COIN_SYMBOL]["unsubscribeFromNewBlocks"](
        newBlocksSub,
        {
            "id": 0,
            "params": {}
        },
        config
    )

    if not got["unsubscribed"]:
        logger.printError(f"Error in unsubscribe from new blocks. Expected: True Got: {got['unsubscribed']}")
        assert False

    got = wsMethods[COIN_SYMBOL]["unsubscribeFromNewBlocks"](
        newBlocksSub,
        {
            "id": 0,
            "params": {}
        },
        config
    )

    if got["unsubscribed"]:
        logger.printError(f"Error in unsubscribe from new blocks. Expected: False Got: {got['unsubscribed']}")
        assert False

    assert True
