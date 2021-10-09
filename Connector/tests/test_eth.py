import pytest
import threading
from Connector import server
from rpcutils.rpcutils import RPCMethods

@pytest.fixture
def app():
    serverThread = threading.Thread(server.runServer)
    serverThread.start()
    return

@pytest.fixture
def rpcMethods():
    return RPCMethods

def test1(rpcMethods):
    assert True