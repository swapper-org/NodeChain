#!/usr/bin/python3
import os


RPC_ETHEREUM_PORT = 8545
RPC_ETHEREUM_HOST = "ethereumgo"

RPC_ENDPOINT = "http://{}:{}".format(RPC_ETHEREUM_HOST, RPC_ETHEREUM_PORT)

if os.getenv("NETWORK", "regtest") != "regtest":
    WS_ETHEREUM_PORT = 8546
else:
    WS_ETHEREUM_PORT = 8545

WS_ENDPOINT = "ws://{}:{}".format(RPC_ETHEREUM_HOST, WS_ETHEREUM_PORT)
