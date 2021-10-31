from decimal import Decimal
import pytest
import threading
import json
import server
from btc.connector import RPC_CORE_ENDPOINT
from btc.constants import *
from logger import logger
from rpcutils.rpcconnector import RPCConnector
from rpcutils.rpcutils import RPCMethods
from wsutils.serverwebsocket import ServerWebSocket
from wsutils.wsutils import webSocketMethods
from wsutils.constants import *


def makeBitcoinCoreTransaction(method, params):
    
    try:
        return RPCConnector.request(RPC_CORE_ENDPOINT, 1, method, params)
    except Exception as err:
        logger.printError(f"Can not make request to {RPC_CORE_ENDPOINT}. {err}")
        assert False


def mineBlocksToAddress(address, numBlocks=1):
    return makeBitcoinCoreTransaction("generatetoaddress", [numBlocks, address])



wallet1Name = "wallet1"
makeBitcoinCoreTransaction("createwallet", [wallet1Name])
address1 = makeBitcoinCoreTransaction("getnewaddress", [])
privateKey1 = makeBitcoinCoreTransaction("dumpprivkey", [address1])
address2 = makeBitcoinCoreTransaction("getnewaddress", [])
minerAddress = makeBitcoinCoreTransaction("getnewaddress", [])
refundAddress1 = makeBitcoinCoreTransaction("getnewaddress", [])
serverWebSocket = ServerWebSocket()

mineBlocksToAddress(address1, 150)
mineBlocksToAddress(address2, 150)


@pytest.fixture
def app():
    serverThread = threading.Thread(server.runServer)
    serverThread.start()
    return


def sendTransaction(fromAddress, toAddress, amount):

    signedRawTransaction, ok = createSignedRawTransaction(fromAddress, toAddress, amount)
    
    if not ok:
        return None, False
    
    if makeBitcoinCoreTransaction("testmempoolaccept", [[signedRawTransaction[HEX]]]):
        return makeBitcoinCoreTransaction("sendrawtransaction", [signedRawTransaction[HEX]]), True


def createSignedRawTransaction(fromAddress, toAddress, amount):
    
    adddressUtxos = makeBitcoinCoreTransaction("listunspent", [1, 9999999, [fromAddress]])

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


    rawTransaction = makeBitcoinCoreTransaction("createrawtransaction",
        [
            [{key: transactionUtxo[key] for key in (TX_ID, VOUT) if key in transactionUtxo} for transactionUtxo in transactionUtxos],
            [{toAddress: amount}],
            0,
            True
        ]
    )
    fundTransactionResponse = makeBitcoinCoreTransaction("fundrawtransaction",
        [
            rawTransaction,
            {
                "changeAddress": refundAddress1,
                "includeWatching": False,
                "feeRate": 0.00005,
                "replaceable": True,
                "changePosition": 1,
                "subtractFeeFromOutputs": [0]
            }
        ]
    )

    signedRawTransaction = makeBitcoinCoreTransaction("signrawtransactionwithwallet",
        [
            fundTransactionResponse[HEX],
            [{key: transactionUtxo[key] for key in (TX_ID, VOUT, AMOUNT, SCRIPT_PUB_KEY) if key in transactionUtxo} for transactionUtxo in transactionUtxos]
        ]
    )

    if signedRawTransaction["complete"]:
        return signedRawTransaction, True

    return None, False


def simulateTransactions(numTransations = 100, amount = 0.01, transactionsPerBlock = 5, minerAddress = minerAddress):


    for i in range(numTransations):
        
        transaction, ok = sendTransaction(address1, address2, amount)

        if not ok:
            break

        logger.printInfo(f"Transaction {i} done: {transaction}")

        if i % transactionsPerBlock == 0:
            makeBitcoinCoreTransaction("generatetoaddress", [1, minerAddress])
            logger.printInfo(f"New block generated")

    
    makeBitcoinCoreTransaction("generatetoaddress", [1, minerAddress])
    logger.printInfo(f"New block generated")


def testGetBlock():
    
    if "getBlockByNumber" not in RPCMethods:
        logger.printError(f"getBlockByNumber not loaded in RPCMethods")
        assert False
    
    if "getBlockByHash" not in RPCMethods:
        logger.printError(f"getBlockByHash not loaded in RPCMethods")
        assert False

    blockNumber = 1

    expectedHash = makeBitcoinCoreTransaction(GET_BLOCK_HASH_METHOD, [blockNumber])
    expectedBlock = makeBitcoinCoreTransaction(GET_BLOCK_METHOD, [expectedHash, 2])

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
        logger.printError(f"getHeight not loaded in RPCMethods")
        assert False
    

    expectedHeight = makeBitcoinCoreTransaction(GET_BLOCK_COUNT_METHOD, [])
    expectedHash = makeBitcoinCoreTransaction(GET_BLOCK_HASH_METHOD, [expectedHeight])

    got = RPCMethods["getHeight"](0, {})

    assert got[LATEST_BLOCK_INDEX] == expectedHeight and got[LATEST_BLOCK_HASH] == expectedHash


def testGetFeePerByte():
    
    if "getFeePerByte" not in RPCMethods:
        logger.printError(f"getFeePerByte not loaded in RPCMethods")
        assert False
    
    simulateTransactions()
    
    confirmations = 2
    expected = makeBitcoinCoreTransaction(ESTIMATE_SMART_FEE_METHOD, [confirmations])
    got = RPCMethods["getFeePerByte"](0, {
        CONFIRMATIONS: str(confirmations)
    })

    assert str(expected[FEE_RATE]) == str(float((Decimal(got[FEE_PER_BYTE]) / 100000000)))


def testBroadcastTransaction():
    
    if "broadcastTransaction" not in RPCMethods:
        logger.printError(f"broadcastTransaction not loaded in RPCMethods")
        assert False

    signedRawTransaction, ok = createSignedRawTransaction(address1, address2, 115)

    if not ok:
        logger.printError(f"Can not create transaction to broadcasts")
        assert False

    RPCMethods["broadcastTransaction"](0, {
        RAW_TRANSACTION: signedRawTransaction[HEX]
    })

    blockMinedHash = mineBlocksToAddress(minerAddress, 1)[0]
    blockMined = makeBitcoinCoreTransaction(GET_BLOCK_METHOD, [blockMinedHash, 2])


    found = signedRawTransaction[HEX] in [tx[HEX] for tx in blockMined[TX]]

    """found = False
    for transaction in blockMined[TX]:
        if transaction[HEX] == signedRawTransaction[HEX]:
            found = True
            assert True"""

    if not found:
        logger.printError(f"Signed raw transaction {signedRawTransaction[HEX]} not found in last generated block {blockMinedHash}")
    assert found


def testSubscribeAddressBalance():

    if "subscribeAddressBalance" not in webSocketMethods:
        logger.printError("Method subscribeAddressBalance not loaded")
        assert False
    
    got = webSocketMethods["subscribeAddressBalance"](serverWebSocket, 0, {
        ADDRESS: address1
    })

    if not got[SUBSCRIBED]:
        logger.printError(f"Error in subscribe to address balace. Expected: True Got: {got[SUBSCRIBED]}")
        assert False
    
    got = webSocketMethods["subscribeAddressBalance"](serverWebSocket, 0, {
        ADDRESS: address1
    })

    if got[SUBSCRIBED]:
        logger.printError(f"Error in subscribe to address balace. Expected: False Got: {got[SUBSCRIBED]}")
        assert False

    assert True


def testUnsubscribeAddressBalance():

    if "unsubscribeAddressBalance" not in webSocketMethods:
        logger.printError("Method unsubscribeAddressBalance not loaded")
        assert False

    got = webSocketMethods["unsubscribeAddressBalance"](serverWebSocket, 0, {
        ADDRESS: address1
    })

    if not got[UNSUBSCRIBED]:
        logger.printError(f"Error in unsubscribe to address balace. Expected: True Got: {got[UNSUBSCRIBED]}")
        assert False
    
    got = webSocketMethods["unsubscribeAddressBalance"](serverWebSocket, 0, {
        ADDRESS: address1
    })

    if got[UNSUBSCRIBED]:
        logger.printError(f"Error in unsubscribe to address balace. Expected: False Got: {got[UNSUBSCRIBED]}")
        assert False
    
    assert True