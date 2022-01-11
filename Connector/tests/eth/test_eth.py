#!/usr/bin/python3
import json
import pytest
import time
from web3 import Web3
from eth.connector import RPC_ENDPOINT
from eth.constants import *
from eth import utils
from logger import logger
from rpcutils.rpcutils import RPCMethods
from rpcutils.rpcconnector import RPCConnector
from wsutils.constants import *
from wsutils.wsutils import webSocketMethods, webSockets
from wsutils.subscribers import ListenerSubscriber

for webSocket in webSockets:
    webSocket()

address1 = "0x625ACaEdeF812d2842eFd2Fb0294682A868455bd"
privateKey1 = "0x6fa76995e9a39e852f893e8347c662453a5d517846d150bdf3ddf7601c4bc74c"

address2 = "0x93261B4021dbd6200Df9B36B151f4ECF34889e94"

sub = ListenerSubscriber()
newBlocksSub = ListenerSubscriber()


def makeTransaction(address1=address1, address2=address2, value=1, gas=2000000):

    web3 = Web3(Web3.HTTPProvider(RPC_ENDPOINT))

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
        return RPCConnector.request(RPC_ENDPOINT, 1, method, params)
    except Exception as err:
        logger.printError(f"Can not make request to {RPC_ENDPOINT}. {err}")
        assert False


def testGetAddressBalance():

    if "getAddressBalance" not in RPCMethods:
        logger.printError("Method getAddressBalance not loaded")
        assert False

    expectedLatest = makeEtherumgoRequest(
        GET_BALANCE_METHOD,
        [address1, LATEST]
    )

    expectedPending = makeEtherumgoRequest(
        GET_BALANCE_METHOD,
        [address1, PENDING]
    )

    got = RPCMethods["getAddressBalance"](0, {"address": address1})

    assert got[BALANCE][CONFIRMED] == str(int(expectedPending, 16)) and got[BALANCE][UNCONFIRMED] == str(int(expectedPending, 16) - int(expectedLatest, 16)) and address1 == got[ADDRESS]


def testGetAddressesBalance():

    if "getAddressesBalance" not in RPCMethods:
        logger.printError("Method getAddressBalance not loaded")
        assert False

    addresses = [address1, address2]

    got = RPCMethods["getAddressesBalance"](0, {"addresses": addresses})

    for address in addresses:

        expectedLatest = makeEtherumgoRequest(
            GET_BALANCE_METHOD,
            [address, LATEST]
        )
        expectedPending = makeEtherumgoRequest(
            GET_BALANCE_METHOD,
            [address, PENDING]
        )

        found = False
        for gotBalance in got:

            if gotBalance[ADDRESS] == address:
                found = True
                if not (gotBalance[BALANCE][CONFIRMED] == str(int(expectedPending, 16)) and gotBalance[BALANCE][UNCONFIRMED] == str(int(expectedPending, 16) - int(expectedLatest, 16))):
                    logger.printError(f"Error validating {address}")
                    assert False
        if not found:
            logger.printError(f"Can not find balance for {address}")
            assert False

    assert True


def testGetHeight():

    if "getHeight" not in RPCMethods:
        logger.printError("Method getHeight not loaded")
        assert False

    got = RPCMethods["getHeight"](0, {})

    expected = makeEtherumgoRequest(
        GET_BLOCK_BY_NUMBER_METHOD,
        [LATEST, True]
    )

    assert str(int(expected[NUMBER], 16)) == got[LATEST_BLOCK_INDEX] and expected[HASH] == got[LATEST_BLOCK_HASH]


def testGetTransaction():

    if "getTransaction" not in RPCMethods:
        logger.printError("Method getTransaction not loaded")
        assert False

    _, txHash = makeTransaction()

    got = RPCMethods["getTransaction"](0, {
        TX_HASH: txHash.hex()
    })

    expected = makeEtherumgoRequest(GET_TRANSACTION_BY_HASH_METHOD, [txHash.hex()])

    assert json.dumps(got[TRANSACTION]["data"], sort_keys=True) == json.dumps(expected, sort_keys=True)
    assert got[TRANSACTION][BLOCK_HASH] == expected[BLOCK_HASH]
    assert got[TRANSACTION]["fee"] == utils.toHex(utils.toWei(expected["gas"]) * utils.toWei(expected["gasPrice"]))

    for transfer in got[TRANSACTION]["transfers"]:
        assert transfer[TO] == expected[TO]
        assert transfer[FROM] == expected[FROM]
        assert transfer[AMOUNT] == expected[VALUE]
        assert transfer["fee"] == utils.toHex(utils.toWei(expected["gas"]) * utils.toWei(expected["gasPrice"]))


def testEstimateGas():

    if "estimateGas" not in RPCMethods:
        logger.printError("Method estimateGas not loaded")
        assert False

    web3 = Web3(Web3.HTTPProvider(RPC_ENDPOINT))

    nonce = web3.eth.getTransactionCount(address1)

    tx = {
        "nonce": nonce,
        "to": address2,
        "value": str(web3.toWei(1, 'ether')),
        "gas": "2000000",
        "gasPrice": str(web3.toWei('50', 'gwei'))
    }

    got = RPCMethods["estimateGas"](0, {
        TX: tx
    })
    expected = makeEtherumgoRequest(ESTIMATE_GAS_METHOD, [tx])

    assert got[ESTIMATED_GAS] == str(int(expected, 16))


def testGetGasPrice():

    if "getGasPrice" not in RPCMethods:
        logger.printError("Method getGasPrice not loaded")
        assert False

    got = RPCMethods["getGasPrice"](0, {

    })
    expected = makeEtherumgoRequest(
        GET_GAS_PRICE_METHOD,
        None
    )

    assert str(int(expected, 16)) == got[GAS_PRICE]


def testGetTransactionReceipt():

    if "getTransactionReceipt" not in RPCMethods:
        logger.printError("Method getTransactionReceipt not loaded")
        assert False

    _, txHash = makeTransaction()
    got = RPCMethods["getTransactionReceipt"](0, {TX_HASH: txHash.hex()})
    expected = makeEtherumgoRequest(GET_TRANSACTION_RECEIPT_METHOD, [txHash.hex()])

    for key in expected:
        if key not in got:
            logger.printError(f"{key} not found in Connector response")
            assert False
        if got[key] != expected[key]:
            logger.printError("Transaction receipt data not correct")
            assert False

    assert True


def testGetTransactionCount():

    if "getTransactionCount" not in RPCMethods:
        logger.printError("Method getTransactionCount not loaded")
        assert False

    got = RPCMethods["getTransactionCount"](0, {
        ADDRESS: address1,
        PENDING: True
    })
    expected = makeEtherumgoRequest(GET_TRANSACTION_COUNT_METHOD, [address1, PENDING])

    assert got[TRANSACTION_COUNT] == str(int(expected, 16))


def testGetBlock():

    if "getBlockByNumber" not in RPCMethods:
        logger.printError("Method getBlockByNumber not loaded")
        assert False

    if "getBlockByHash" not in RPCMethods:
        logger.printError("Method getBlockByHash not loaded")
        assert False

    expected = makeEtherumgoRequest(GET_BLOCK_BY_NUMBER_METHOD, ["0x1", True])

    gotBlockByNumber = RPCMethods["getBlockByNumber"](0, {
        BLOCK_NUMBER: "1"
    })

    gotBlockByHash = RPCMethods["getBlockByHash"](0, {
        BLOCK_HASH: expected[HASH]
    })

    if not json.dumps(expected[TRANSACTIONS], sort_keys=True) == json.dumps(gotBlockByNumber[TRANSACTIONS], sort_keys=True):
        logger.printError("getBlockByNumber failed")
        assert False

    if not json.dumps(expected[TRANSACTIONS], sort_keys=True) == json.dumps(gotBlockByHash[TRANSACTIONS], sort_keys=True):
        logger.printError("getBlockByHash failed")
        assert False

    assert True


def testBroadCastTransaction():

    if "broadcastTransaction" not in RPCMethods:
        logger.printError("Method broadcastTransaction not loaded")
        assert False

    if "getTransaction" not in RPCMethods:
        logger.printError("Method getTransaction not loaded")
        assert False

    web3 = Web3(Web3.HTTPProvider(RPC_ENDPOINT))

    nonce = web3.eth.getTransactionCount(address1)

    tx = {
        "nonce": nonce,
        "to": address2,
        "value": web3.toWei(1, 'ether'),
        "gas": 2000000,
        "gasPrice": web3.toWei('50', 'gwei')
    }

    signedTx = web3.eth.account.sign_transaction(tx, privateKey1)

    got = RPCMethods["broadcastTransaction"](0, {
        RAW_TRANSACTION: signedTx.rawTransaction.hex()
    })

    expected = makeEtherumgoRequest(GET_TRANSACTION_BY_HASH_METHOD, [got[BROADCASTED]])

    assert got[BROADCASTED] == expected[HASH]


def testSubscribeAddressBalance():

    if "subscribeToAddressBalance" not in webSocketMethods:
        logger.printError("Method subscribeToAddressBalance not loaded")
        assert False

    got = webSocketMethods["subscribeToAddressBalance"](sub, 0, {
        ADDRESS: address1
    })

    if not got[SUBSCRIBED]:
        logger.printError(f"Error in subscribe to address balance. Expected: True Got: {got[SUBSCRIBED]}")
        assert False

    got = webSocketMethods["subscribeToAddressBalance"](sub, 0, {
        ADDRESS: address1
    })

    if got[SUBSCRIBED]:
        logger.printError(f"Error in subscribe to address balance. Expected: False Got: {got[SUBSCRIBED]}")
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

    if "unsubscribeFromAddressBalance" not in webSocketMethods:
        logger.printError("Method unsubscribeFromAddressBalance not loaded")
        assert False

    got = webSocketMethods["unsubscribeFromAddressBalance"](sub, 0, {
        ADDRESS: address1
    })

    if not got[UNSUBSCRIBED]:
        logger.printError(f"Error in unsubscribe from address balance. Expected: True Got: {got[UNSUBSCRIBED]}")
        assert False

    got = webSocketMethods["unsubscribeFromAddressBalance"](sub, 0, {
        ADDRESS: address1
    })

    if got[UNSUBSCRIBED]:
        logger.printError(f"Error in unsubscribe from address balance. Expected: False Got: {got[UNSUBSCRIBED]}")
        assert False

    assert True


def testSubscribeToNewBlocks():

    if "subscribeToNewBlocks" not in webSocketMethods:
        logger.printError("Method subscribeToNewBlocks not loaded")
        assert False

    got = webSocketMethods["subscribeToNewBlocks"](newBlocksSub, 0, {})

    if not got[SUBSCRIBED]:
        logger.printError(f"Error in subscribe to new blocks. Expected: True Got: {got[SUBSCRIBED]}")
        assert False

    got = webSocketMethods["subscribeToNewBlocks"](newBlocksSub, 0, {})

    if got[SUBSCRIBED]:
        logger.printError(f"Error in subscribe to new blocks. Expected: False Got: {got[SUBSCRIBED]}")
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

    if "unsubscribeFromNewBlocks" not in webSocketMethods:
        logger.printError("Method unsubscribeFromNewBlocks not loaded")
        assert False

    got = webSocketMethods["unsubscribeFromNewBlocks"](newBlocksSub, 0, {})

    if not got[UNSUBSCRIBED]:
        logger.printError(f"Error in unsubscribe from new blocks. Expected: True Got: {got[UNSUBSCRIBED]}")
        assert False

    got = webSocketMethods["unsubscribeFromNewBlocks"](newBlocksSub, 0, {})

    if got[UNSUBSCRIBED]:
        logger.printError(f"Error in unsubscribe from new blocks. Expected: False Got: {got[UNSUBSCRIBED]}")
        assert False

    assert True
