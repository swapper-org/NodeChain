#!/usr/bin/python3
from decimal import Decimal
import pytest
import json
import time
from btc.connector import RPC_CORE_ENDPOINT, RPC_ELECTRUM_ENDPOINT
from btc.constants import *
from btc.utils import convertToSatoshi
from logger import logger
from rpcutils.rpcconnector import RPCConnector
from rpcutils.rpcutils import RPCMethods
from rpcutils.errorhandler import BadRequestError
from wsutils.subscribers import ListenerSubscriber
from wsutils.wsutils import webSocketMethods
from wsutils.constants import *


def makeRequest(endpoint, method, params):
    return RPCConnector.request(endpoint, 1, method, params)


def makeBitcoinCoreRequest(method, params):
    return makeRequest(RPC_CORE_ENDPOINT, method, params)


def makeElectrumRequest(method, params):
    return makeRequest(RPC_ELECTRUM_ENDPOINT, method, params)


def mineBlocksToAddress(address, numBlocks=1):
    return makeBitcoinCoreRequest("generatetoaddress", [numBlocks, address])


wallet1Name = "wallet1"
try:
    makeBitcoinCoreRequest("loadwallet", [wallet1Name])
except BadRequestError:
    if wallet1Name not in makeBitcoinCoreRequest("listwallets", []):
        makeBitcoinCoreRequest("createwallet", [wallet1Name])

address1 = makeBitcoinCoreRequest("getnewaddress", [])
privateKey1 = makeBitcoinCoreRequest("dumpprivkey", [address1])
address2 = makeBitcoinCoreRequest("getnewaddress", [])
minerAddress = makeBitcoinCoreRequest("getnewaddress", [])
refundAddress1 = makeBitcoinCoreRequest("getnewaddress", [])
sub = ListenerSubscriber()
newBlocksSub = ListenerSubscriber()
mineBlocksToAddress(address1, 150)
mineBlocksToAddress(address2, 150)


def sendTransaction(fromAddress, toAddress, amount):

    signedRawTransaction, ok = createSignedRawTransaction(fromAddress, toAddress, amount)

    if not ok:
        return None, False

    if makeBitcoinCoreRequest("testmempoolaccept", [[signedRawTransaction[HEX]]]):
        return makeBitcoinCoreRequest("sendrawtransaction", [signedRawTransaction[HEX]]), True


def createSignedRawTransaction(fromAddress, toAddress, amount):

    adddressUtxos = makeBitcoinCoreRequest("listunspent", [1, 9999999, [fromAddress]])

    amountCount = 0
    transactionUtxos = []
    allowed = False

    for addressUtxo in adddressUtxos:

        amountCount += addressUtxo[AMOUNT]
        transactionUtxos.append({
            TX_ID: addressUtxo[TX_ID],
            VOUT: addressUtxo[VOUT],
            AMOUNT: addressUtxo[AMOUNT],
            SCRIPT_PUB_KEY: addressUtxo[SCRIPT_PUB_KEY]
        })

        if amountCount > amount:
            allowed = True
            break

    if not allowed:
        logger.printError(f"Transaction without {amount} fund")
        return None, False

    rawTransaction = makeBitcoinCoreRequest("createrawtransaction", [
        [{key: transactionUtxo[key] for key in (TX_ID, VOUT) if key in transactionUtxo} for transactionUtxo in transactionUtxos],
        [{toAddress: amount}],
        0,
        True
    ])

    fundTransactionResponse = makeBitcoinCoreRequest("fundrawtransaction", [
        rawTransaction,
        {
            "changeAddress": refundAddress1,
            "includeWatching": False,
            "feeRate": 0.00005,
            "replaceable": True,
            "changePosition": 1,
            "subtractFeeFromOutputs": [0]
        }
    ])

    signedRawTransaction = makeBitcoinCoreRequest("signrawtransactionwithwallet", [
        fundTransactionResponse[HEX],
        [{key: transactionUtxo[key] for key in (TX_ID, VOUT, AMOUNT, SCRIPT_PUB_KEY) if key in transactionUtxo} for transactionUtxo in transactionUtxos]
    ])

    if signedRawTransaction["complete"]:
        return signedRawTransaction, True

    return None, False


def simulateTransactions(numTransations=100, amount=0.01, transactionsPerBlock=5, minerAddress=minerAddress):

    for i in range(numTransations):

        transaction, ok = sendTransaction(address1, address2, amount)

        if not ok:
            break

        logger.printInfo(f"Transaction {i} done: {transaction}")

        if i % transactionsPerBlock == 0:
            makeBitcoinCoreRequest("generatetoaddress", [1, minerAddress])
            logger.printInfo("New block generated")

    makeBitcoinCoreRequest("generatetoaddress", [1, minerAddress])
    logger.printInfo("New block generated")


def testGetBlock():

    if "getBlockByNumber" not in RPCMethods:
        logger.printError("getBlockByNumber not loaded in RPCMethods")
        assert False

    if "getBlockByHash" not in RPCMethods:
        logger.printError("getBlockByHash not loaded in RPCMethods")
        assert False

    blockNumber = 1

    expectedHash = makeBitcoinCoreRequest(GET_BLOCK_HASH_METHOD, [blockNumber])
    expectedBlock = makeBitcoinCoreRequest(GET_BLOCK_METHOD, [expectedHash, 2])

    gotByHash = RPCMethods["getBlockByHash"](0, {
        BLOCK_HASH: expectedHash
    })

    if not json.dumps(expectedBlock, sort_keys=True) == json.dumps(gotByHash, sort_keys=True):
        logger.printError(f"Get block by hash error. Expected  {expectedBlock} but Got{gotByHash}")
        assert False

    gotByNumber = RPCMethods["getBlockByNumber"](0, {
        BLOCK_NUMBER: str(blockNumber)
    })

    if not json.dumps(expectedBlock, sort_keys=True) == json.dumps(gotByNumber, sort_keys=True):
        logger.printError(f"Get block by number error. Expected  {expectedBlock} but Got{gotByNumber}")
        assert False

    assert True


def testGetHeight():

    if "getHeight" not in RPCMethods:
        logger.printError("getHeight not loaded in RPCMethods")
        assert False

    expectedHeight = makeBitcoinCoreRequest(GET_BLOCK_COUNT_METHOD, [])
    expectedHash = makeBitcoinCoreRequest(GET_BLOCK_HASH_METHOD, [expectedHeight])

    got = RPCMethods["getHeight"](0, {})

    assert got[LATEST_BLOCK_INDEX] == expectedHeight and got[LATEST_BLOCK_HASH] == expectedHash


def testGetFeePerByte():

    if "getFeePerByte" not in RPCMethods:
        logger.printError("getFeePerByte not loaded in RPCMethods")
        assert False

    simulateTransactions(numTransations=50)

    confirmations = 2
    expected = makeBitcoinCoreRequest(ESTIMATE_SMART_FEE_METHOD, [confirmations])
    got = RPCMethods["getFeePerByte"](0, {
        CONFIRMATIONS: str(confirmations)
    })

    assert str(expected[FEE_RATE]) == str(float((Decimal(got[FEE_PER_BYTE]) / 100000000)))


def testBroadcastTransaction():

    if "broadcastTransaction" not in RPCMethods:
        logger.printError("broadcastTransaction not loaded in RPCMethods")
        assert False

    signedRawTransaction, ok = createSignedRawTransaction(address1, address2, 115)

    if not ok:
        logger.printError("Can not create transaction to broadcasts")
        assert False

    RPCMethods["broadcastTransaction"](0, {
        RAW_TRANSACTION: signedRawTransaction[HEX]
    })

    blockMinedHash = mineBlocksToAddress(minerAddress, 1)[0]
    blockMined = makeBitcoinCoreRequest(GET_BLOCK_METHOD, [blockMinedHash, 2])

    found = signedRawTransaction[HEX] in [tx[HEX] for tx in blockMined[TX]]

    if not found:
        logger.printError(f"Signed raw transaction {signedRawTransaction[HEX]} not found in last generated block {blockMinedHash}")
    assert found


def testGetAddressHistory():

    if "getAddressHistory" not in RPCMethods:
        logger.printError("getAddressHistory not loaded in RPCMethods")
        assert False

    expected = makeElectrumRequest(GET_ADDRESS_HISTORY_METHOD, [address1])

    got = RPCMethods["getAddressHistory"](0, {
        ADDRESS: address1
    })

    expectedTxHashes = {item[TX_HASH_SNAKE_CASE]: False for item in expected}

    for gotTxHash in got[TX_HASHES]:
        if gotTxHash in expectedTxHashes:
            expectedTxHashes[gotTxHash] = True
        else:
            logger.printError(f"Transaction {gotTxHash} not in expected txHashes {expectedTxHashes}")
            assert False

    for expectedTxHash in expectedTxHashes:
        if not expectedTxHashes[expectedTxHash]:
            logger.printError(f"Transaction {expectedTxHash} not in got txHashes {got[TX_HASHES]}")
            assert False

    assert True


def testGetAddressBalance():

    if "getAddressBalance" not in RPCMethods:
        logger.printError("getAddressBalance not loaded in RPCMethods")
        assert False

    expected = makeElectrumRequest("getaddressbalance", [address1])
    got = RPCMethods["getAddressBalance"](0, {
        ADDRESS: address1
    })

    assert convertToSatoshi(expected[CONFIRMED]) == got[BALANCE][CONFIRMED] and convertToSatoshi(expected[UNCONFIRMED]) == got[BALANCE][UNCONFIRMED] and address1 == got[ADDRESS]


def testGetAddressesBalance():

    if "getAddressesBalance" not in RPCMethods:
        logger.printError("getAddressesBalance not loaded in RPCMethods")
        assert False

    addresses = [address1, address2]

    got = RPCMethods["getAddressesBalance"](0, {
        ADDRESSES: addresses
    })

    for addressBalance in got:

        expected = makeElectrumRequest("getaddressbalance", [addressBalance[ADDRESS]])

        if convertToSatoshi(expected[CONFIRMED]) != addressBalance[BALANCE][CONFIRMED] or convertToSatoshi(expected[UNCONFIRMED]) != addressBalance[BALANCE][UNCONFIRMED]:
            logger.printError(f"Error getting balance for {addressBalance[ADDRESS]}. Expected: {expected}. Got: {addressBalance[BALANCE]}")
            assert False

    assert True


def testGetTransactionHex():

    if "getTransactionHex" not in RPCMethods:
        logger.printError("getTransactionHex not loaded in RPCMethods")
        assert False

    addressHistory = makeElectrumRequest(GET_ADDRESS_HISTORY_METHOD, [address1])
    txHash = addressHistory[0][TX_HASH_SNAKE_CASE]

    expected = makeElectrumRequest(GET_TRANSACTION_METHOD, [txHash])

    got = RPCMethods["getTransactionHex"](0, {
        TX_HASH: txHash
    })

    assert expected == got[RAW_TRANSACTION]


def testGetTransactionCount():

    if "getTransactionCount" not in RPCMethods:
        logger.printError("getTransactionCount not loaded in RPCMethods")
        assert False

    pending = True

    expected = makeElectrumRequest(GET_ADDRESS_HISTORY_METHOD, [address1])
    got = RPCMethods["getTransactionCount"](0, {
        ADDRESS: address1,
        PENDING: pending
    })

    pendingCount = 0
    for tx in expected:
        if tx[HEIGHT] == 0:
            pendingCount += 1

    assert got[TRANSACTION_COUNT] == str(pendingCount) if pending else str(len(expected) - pendingCount)


def testGetAddressUnspent():

    if "getAddressUnspent" not in RPCMethods:
        logger.printError("getAddressUnspent not loaded in RPCMethods")
        assert False

    expected = makeElectrumRequest(GET_ADDRESS_UNSPENT_METHOD, [address1])

    got = RPCMethods["getAddressUnspent"](0, {
        ADDRESS: address1
    })

    txs = []

    for tx in expected:
        txs.append(
            {
                TX_HASH: tx[TX_HASH_SNAKE_CASE],
                VOUT: str(tx[TX_POS_SNAKE_CASE]),
                STATUS: {
                    CONFIRMED: tx[HEIGHT] != 0,
                    BLOCK_HEIGHT: str(tx[HEIGHT])
                },
                VALUE: str(tx[VALUE])
            }
        )

    assert json.dumps(got, sort_keys=True) == json.dumps(txs, sort_keys=True)


def testGetTransaction():

    if "getTransaction" not in RPCMethods:
        logger.printError("getTransaction not loaded in RPCMethods")
        assert False

    addressHistory = makeElectrumRequest(GET_ADDRESS_HISTORY_METHOD, [address1])
    txHash = addressHistory[0][TX_HASH_SNAKE_CASE]

    rawTransaction = makeElectrumRequest(GET_TRANSACTION_METHOD, [txHash])
    expected = makeBitcoinCoreRequest(DECODE_RAW_TRANSACTION_METHOD, [rawTransaction])

    got = RPCMethods["getTransaction"](0, {
        TX_HASH: txHash
    })

    assert json.dumps(expected, sort_keys=True) == json.dumps(got, sort_keys=True)


def testSubscribeToAddressBalance():

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

    got = webSocketMethods["unsubscribeAddressBalance"](sub, 0, {
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
    mineBlocksToAddress(address1, 1)

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
