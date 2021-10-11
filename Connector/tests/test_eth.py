import pytest
import threading
from Connector import server
from Connector.rpcutils.constants import RESULT
from logger import logger
from rpcutils.rpcutils import RPCMethods
from rpcutils.rpcconnector import RPCConnector
from eth.connector import RPC_ENDPOINT
from eth.constants import *

@pytest.fixture
def app():
    serverThread = threading.Thread(server.runServer)
    serverThread.start()
    return

@pytest.fixture
def rpcMethods():
    return RPCMethods


def makeEtherumgoRequest(method, params):

    try:
        return RPCConnector.request(RPC_ENDPOINT, 1, method, params)
    except Exception as err:
        logger.printError(f"Can not make request to {RPC_ENDPOINT}. {err}")
        assert False


def testGetAddressBalance(rpcMethods):
    
    if "getAddressBalance" not in rpcMethods:
        logger.printError("Method getAddressBalance not loaded")
        assert False
    
    address = "0x625ACaEdeF812d2842eFd2Fb0294682A868455bd"
    
    latestResponse = makeEtherumgoRequest(
        GET_BALANCE_METHOD, 
        [address, LATEST]
    )
    pendingResponse = makeEtherumgoRequest(
        GET_BALANCE_METHOD, 
        [address, PENDING]
    )
    
    connectorResponse = rpcMethods["getAddressBalance"](0, {"address" : address})

    assert connectorResponse[CONFIRMED] == pendingResponse and connectorResponse[UNCONFIRMED] == (hex(int(pendingResponse, 16) - int(latestResponse, 16)))


def testGetAddressesBalance(rpcMethods):
    
    if "getAddressesBalance" not in rpcMethods:
        logger.printError("Method getAddressBalance not loaded")
        assert False
    
    addresses = ["0x625ACaEdeF812d2842eFd2Fb0294682A868455bd",
                 "0x93261B4021dbd6200Df9B36B151f4ECF34889e94"]

    connectorResponse = rpcMethods["getAddressesBalance"](0, {"addresses" : addresses})

    for address in addresses:

        latestResponse = makeEtherumgoRequest(
            GET_BALANCE_METHOD, 
            [address, LATEST]
        )
        pendingResponse = makeEtherumgoRequest(
            GET_BALANCE_METHOD, 
            [address, PENDING]
        )

        for addressBalance in connectorResponse:
            if not addressBalance[BALANCE][CONFIRMED] == pendingResponse and addressBalance[BALANCE][UNCONFIRMED] == (hex(int(pendingResponse, 16) - int(latestResponse, 16))):
                logger.printError(f"Error validating {address}")
                assert False

    assert True


def testGetHeight(rpcMethods):

    if "getHeight" not in rpcMethods:
        logger.printError("Method getHeight not loaded")
        assert False

    connectorResponse = rpcMethods["getHeight"](0, {})
    nodeResponse = makeEtherumgoRequest(
            GET_BLOCK_BY_NUMBER_METHOD, 
            [LATEST, True]
        )

    assert nodeResponse[NUMBER] == connectorResponse[LATEST_BLOCK_INDEX] and nodeResponse[HASH] == connectorResponse[LATEST_BLOCK_HASH]