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
from httputils.httpmethod import RouteTableDef
from httputils.httpconnector import HTTPConnector
from rpcutils.rpcconnector import RPCConnector
from wsutils.wsmethod import RouteTableDef as WsRouteTableDef
from wsutils.subscribers import ListenerSubscriber
from wsutils import websocket


networkName = "regtest"
config = Config(
    coin=COIN_SYMBOL,
    networkName=networkName
)
config.loadConfig(
    config={
        "rpcEndpoint": "http://localhost:8545",
        "wsEndpoint": "http://localhost:8546",
        "indexerEndpoint": "http://localhost:3000"
    }
)

WebSocket(
    coin=COIN_SYMBOL,
    config=config
)

websocket.startWebSockets(COIN_SYMBOL, networkName)


sub = ListenerSubscriber()
newBlocksSub = ListenerSubscriber()


def makeEtherumgoRequest(method, params):

    try:
        return RPCConnector.request(config.rpcEndpoint, 1, method, params)
    except Exception as err:
        logger.printError(f"Can not make request to {config.rpcEndpoint}. {err}")
        assert False


makeEtherumgoRequest("personal_newAccount", [""])
accounts = makeEtherumgoRequest("personal_listAccounts", [])

address1 = accounts[0]
address2 = accounts[1]


def makeTransaction(address1=address1, address2=address2, value=1, gas=2000000):

    txHash = makeEtherumgoRequest(
        "personal_sendTransaction",
        [
            {
                "from": address1,
                "to": address2,
                "value": hex(Web3.toWei(value, "ether")),
                "gas": hex(Web3.toWei(gas, "wei"))
            },
            ""
        ]
    )

    return txHash


def makeHTTPGetRequest(endpoint, path, params):

    try:
        return HTTPConnector.get(
            endpoint=endpoint,
            path=path,
            params=params
        )
    except Exception as err:
        logger.printError(f"Can not make HTTP Get Request to {endpoint}. {err}")
        assert False


def makeHTTPPostRequest(endpoint, path, payload):

    try:
        return HTTPConnector.post(
            endpoint=endpoint,
            path=path,
            json=payload
        )
    except Exception as err:
        logger.printError(f"Can not make HTTP Get Request to {endpoint}. {err}")
        assert False


def testGetAddressBalance():

    if "getAddressBalance" not in RouteTableDef.httpMethods[COIN_SYMBOL]:
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

    got = RouteTableDef.httpMethods[COIN_SYMBOL]["getAddressBalance"].handler({"address": address1}, config)

    assert got["balance"]["confirmed"] == str(int(expectedPending, 16)) and got["balance"]["unconfirmed"] == str(int(expectedPending, 16) - int(expectedLatest, 16)) and address1 == got["address"]


def testGetAddressesBalance():

    if "getAddressesBalance" not in RouteTableDef.httpMethods[COIN_SYMBOL]:
        logger.printError("Method getAddressBalance not loaded")
        assert False

    addresses = [address1, address2]

    got = RouteTableDef.httpMethods[COIN_SYMBOL]["getAddressesBalance"].handler({"addresses": addresses}, config)

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

    if "getHeight" not in RouteTableDef.httpMethods[COIN_SYMBOL]:
        logger.printError("Method getHeight not loaded")
        assert False

    got = RouteTableDef.httpMethods[COIN_SYMBOL]["getHeight"].handler({}, config)

    expected = makeEtherumgoRequest(
        GET_BLOCK_BY_NUMBER_METHOD,
        ["latest", True]
    )

    assert str(int(expected["number"], 16)) == got["latestBlockIndex"] and expected["hash"] == got["latestBlockHash"]


def testGetTransaction():

    if "getTransaction" not in RouteTableDef.httpMethods[COIN_SYMBOL]:
        logger.printError("Method getTransaction not loaded")
        assert False

    txHash = makeTransaction()

    got = RouteTableDef.httpMethods[COIN_SYMBOL]["getTransaction"].handler(
        {
            "txHash": txHash
        },
        config
    )

    expected = makeEtherumgoRequest(GET_TRANSACTION_BY_HASH_METHOD, [txHash])
    expectedBlock = makeEtherumgoRequest(GET_BLOCK_BY_NUMBER_METHOD, [expected["blockNumber"], True])

    assert got["transaction"]["txHash"] == txHash
    assert got["transaction"]["fee"] == str(utils.toWei(expected["gas"]) * utils.toWei(expected["gasPrice"]))
    assert got["transaction"]["blockHash"] == expected["blockHash"]
    assert got["transaction"]["blockNumber"] == str(int(expected["blockNumber"], 16))
    assert got["transaction"]["timestamp"] == str(int(expectedBlock["block"]["timestamp"], 16))
    assert json.dumps(got["transaction"]["data"], sort_keys=True) == json.dumps(expected, sort_keys=True)
    assert json.dumps(got["transaction"]["inputs"][0], sort_keys=True) == json.dumps(
        {
            "address": address1.lower(),
            "amount": str(utils.toWei(expected["value"]))
        },
        sort_keys=True
    )
    assert json.dumps(got["transaction"]["outputs"][0], sort_keys=True) == json.dumps(
        {
            "address": address2.lower(),
            "amount": str(utils.toWei(expected["value"]))
        },
        sort_keys=True
    )


def testGetTransactions():

    if "getTransactions" not in RouteTableDef.httpMethods[COIN_SYMBOL]:
        logger.printError("Method getTransaction not loaded")
        assert False

    txHashes = []
    for i in range(0, 2):
        txHashes.append(makeTransaction())

    got = RouteTableDef.httpMethods[COIN_SYMBOL]["getTransactions"].handler(
        {
            "txHashes": txHashes
        },
        config
    )

    for txHash in txHashes:

        expected = makeEtherumgoRequest(GET_TRANSACTION_BY_HASH_METHOD, [txHash])
        expectedBlock = makeEtherumgoRequest(GET_BLOCK_BY_NUMBER_METHOD, [expected["blockNumber"], True])

        found = False
        for gotTransaction in got["transactions"]:

            if gotTransaction["transaction"]["txHash"] == txHash:
                found = True
                assert gotTransaction["transaction"]["txHash"] == txHash
                assert gotTransaction["transaction"]["fee"] == str(
                    utils.toWei(expected["gas"]) * utils.toWei(expected["gasPrice"]))
                assert gotTransaction["transaction"]["blockHash"] == expected["blockHash"]
                assert gotTransaction["transaction"]["blockNumber"] == str(int(expected["blockNumber"], 16))
                assert gotTransaction["transaction"]["timestamp"] == str(int(expectedBlock["block"]["timestamp"], 16))
                assert json.dumps(gotTransaction["transaction"]["data"], sort_keys=True) == json.dumps(expected, sort_keys=True)
                assert json.dumps(gotTransaction["transaction"]["inputs"][0], sort_keys=True) == json.dumps(
                    {
                        "address": address1.lower(),
                        "amount": str(utils.toWei(expected["value"]))
                    },
                    sort_keys=True
                )
                assert json.dumps(gotTransaction["transaction"]["outputs"][0], sort_keys=True) == json.dumps(
                    {
                        "address": address2.lower(),
                        "amount": str(utils.toWei(expected["value"]))
                    },
                    sort_keys=True
                )
        if not found:
            logger.printError(f"Can not find transaction for {txHash}")
            assert False


def testEstimateGas():

    if "estimateGas" not in RouteTableDef.httpMethods[COIN_SYMBOL]:
        logger.printError("Method estimateGas not loaded")
        assert False

    tx = {
        "from": address1,
        "to": address2,
        "value": hex(Web3.toWei(1, "ether")),
        "gas": hex(Web3.toWei(2000000, "wei"))
    }

    got = RouteTableDef.httpMethods[COIN_SYMBOL]["estimateGas"].handler(
        {
            "tx": tx
        },
        config
    )
    expected = makeEtherumgoRequest(ESTIMATE_GAS_METHOD, [tx])

    assert got["estimatedGas"] == str(int(expected, 16))


def testGetGasPrice():

    if "getGasPrice" not in RouteTableDef.httpMethods[COIN_SYMBOL]:
        logger.printError("Method getGasPrice not loaded")
        assert False

    got = RouteTableDef.httpMethods[COIN_SYMBOL]["getGasPrice"].handler(
        {},
        config
    )
    expected = makeEtherumgoRequest(
        GET_GAS_PRICE_METHOD,
        None
    )

    assert str(int(expected, 16)) == got["gasPrice"]


def testGetTransactionReceipt():

    if "getTransactionReceipt" not in RouteTableDef.httpMethods[COIN_SYMBOL]:
        logger.printError("Method getTransactionReceipt not loaded")
        assert False

    txHash = makeTransaction()
    time.sleep(10)
    got = RouteTableDef.httpMethods[COIN_SYMBOL]["getTransactionReceipt"].handler({"txHash": txHash}, config)
    expected = makeEtherumgoRequest(GET_TRANSACTION_RECEIPT_METHOD, [txHash])

    for key in expected:
        if key not in got:
            logger.printError(f"{key} not found in Connector response")
            assert False
        if got[key] != expected[key]:
            logger.printError("Transaction receipt data not correct")
            assert False

    assert True


def testGetAddressTransactionCount():

    if "getAddressTransactionCount" not in RouteTableDef.httpMethods[COIN_SYMBOL]:
        logger.printError("Method getAddressTransactionCount not loaded")
        assert False

    got = RouteTableDef.httpMethods[COIN_SYMBOL]["getAddressTransactionCount"].handler(
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

    if "getAddressesTransactionCount" not in RouteTableDef.httpMethods[COIN_SYMBOL]:
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

    got = RouteTableDef.httpMethods[COIN_SYMBOL]["getAddressesTransactionCount"].handler(addresses, config)

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

    if "getBlockByNumber" not in RouteTableDef.httpMethods[COIN_SYMBOL]:
        logger.printError("Method getBlockByNumber not loaded")
        assert False

    if "getBlockByHash" not in RouteTableDef.httpMethods[COIN_SYMBOL]:
        logger.printError("Method getBlockByHash not loaded")
        assert False

    expected = makeEtherumgoRequest(GET_BLOCK_BY_NUMBER_METHOD, ["0x1", True])

    gotBlockByNumber = RouteTableDef.httpMethods[COIN_SYMBOL]["getBlockByNumber"].handler({"blockNumber": "1"}, config)

    gotBlockByHash = RouteTableDef.httpMethods[COIN_SYMBOL]["getBlockByHash"].handler({"blockHash": expected["hash"]}, config)

    if not json.dumps(expected["transactions"], sort_keys=True) == json.dumps(gotBlockByNumber["block"]["transactions"], sort_keys=True):
        logger.printError("getBlockByNumber failed")
        assert False

    if not json.dumps(expected["transactions"], sort_keys=True) == json.dumps(gotBlockByHash["block"]["transactions"], sort_keys=True):
        logger.printError("getBlockByHash failed")
        assert False

    assert True


def testBroadCastTransaction():

    if "broadcastTransaction" not in RouteTableDef.httpMethods[COIN_SYMBOL]:
        logger.printError("Method broadcastTransaction not loaded")
        assert False

    if "getTransaction" not in RouteTableDef.httpMethods[COIN_SYMBOL]:
        logger.printError("Method getTransaction not loaded")
        assert False

    tx = {
        "nonce": makeEtherumgoRequest("eth_getTransactionCount", [address1, "latest"]),
        "from": address1,
        "to": address2,
        "value": hex(Web3.toWei(1, "ether")),
        "gas": hex(Web3.toWei(2000000, "wei")),
        "gasPrice": hex(Web3.toWei('50', 'gwei'))
    }

    signedTx = makeEtherumgoRequest("eth_signTransaction", [tx])

    got = RouteTableDef.httpMethods[COIN_SYMBOL]["broadcastTransaction"].handler({"rawTransaction": signedTx["raw"]}, config)

    expected = makeEtherumgoRequest(GET_TRANSACTION_BY_HASH_METHOD, [got["broadcasted"]])

    assert got["broadcasted"] == expected["hash"]


def testGetAddressHistory():

    if "getAddressHistory" not in RouteTableDef.httpMethods[COIN_SYMBOL]:
        logger.printError("Method getAddressHistory not loaded")
        assert False

    for i in range(0, 25):
        makeTransaction()

    time.sleep(10)

    makeEtherumgoRequest("miner_stop", [])

    for i in range(0, 25):
        makeTransaction()

    expectedConfirmed = makeHTTPGetRequest(
        endpoint=config.indexerEndpoint,
        path=INDEXER_TXS_PATH,
        params={
            "and": f"(contract_to.eq.,or(txfrom.eq.{address1},txto.eq.{address1}))"
        }
    )

    expectedPending = makeHTTPPostRequest(
        endpoint=config.rpcEndpoint,
        path=GRAPHQL_PATH,
        payload={
            "query": "query { pending { transactions { hash from { address } to { address } } } }"
        }
    )

    pendingHashes = []

    for tx in expectedPending["data"]["pending"]["transactions"]:
        if tx["from"]["address"] == address1 or tx["to"]["address"] == address1:
            pendingHashes.append(tx["hash"])

    got = RouteTableDef.httpMethods[COIN_SYMBOL]["getAddressHistory"].handler({"address": address1}, config)

    makeEtherumgoRequest("miner_start", [1])

    for tx in expectedConfirmed:
        assert tx["txhash"] in got["txHashes"]

    for hash in pendingHashes:
        assert hash in got["txHashes"]


def testGetAddressesHistory():

    if "getAddressesHistory" not in RouteTableDef.httpMethods[COIN_SYMBOL]:
        logger.printError("Method getAddressesHistory not loaded")
        assert False

    addresses = [address1, address2]

    time.sleep(10)

    got = RouteTableDef.httpMethods[COIN_SYMBOL]["getAddressesHistory"].handler({"addresses": addresses}, config)

    for addrHistory in got:

        expected = makeHTTPGetRequest(
            endpoint=config.indexerEndpoint,
            path=INDEXER_TXS_PATH,
            params={
                "and": f"(contract_to.eq.,or(txfrom.eq.{addrHistory['address']},txto.eq.{addrHistory['address']}))"
            }
        )

        for tx in expected:
            assert tx["txhash"] in addrHistory["txHashes"]


def testSubscribeAddressBalance():

    if "subscribeToAddressBalance" not in WsRouteTableDef.wsMethods[COIN_SYMBOL]:
        logger.printError("Method subscribeToAddressBalance not loaded")
        assert False

    got = WsRouteTableDef.wsMethods[COIN_SYMBOL]["subscribeToAddressBalance"].handler(
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

    got = WsRouteTableDef.wsMethods[COIN_SYMBOL]["subscribeToAddressBalance"].handler(
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

    if "unsubscribeFromAddressBalance" not in WsRouteTableDef.wsMethods[COIN_SYMBOL]:
        logger.printError("Method unsubscribeFromAddressBalance not loaded")
        assert False

    got = WsRouteTableDef.wsMethods[COIN_SYMBOL]["unsubscribeFromAddressBalance"].handler(
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

    got = WsRouteTableDef.wsMethods[COIN_SYMBOL]["unsubscribeFromAddressBalance"].handler(
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

    if "subscribeToNewBlocks" not in WsRouteTableDef.wsMethods[COIN_SYMBOL]:
        logger.printError("Method subscribeToNewBlocks not loaded")
        assert False

    got = WsRouteTableDef.wsMethods[COIN_SYMBOL]["subscribeToNewBlocks"].handler(
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

    got = WsRouteTableDef.wsMethods[COIN_SYMBOL]["subscribeToNewBlocks"].handler(
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

    if "unsubscribeFromNewBlocks" not in WsRouteTableDef.wsMethods[COIN_SYMBOL]:
        logger.printError("Method unsubscribeFromNewBlocks not loaded")
        assert False

    got = WsRouteTableDef.wsMethods[COIN_SYMBOL]["unsubscribeFromNewBlocks"].handler(
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

    got = WsRouteTableDef.wsMethods[COIN_SYMBOL]["unsubscribeFromNewBlocks"].handler(
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
