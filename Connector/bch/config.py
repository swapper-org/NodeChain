#!/usr/bin/python3
from json import JSONEncoder


class Config:

    def __init__(self, coin, networkName):

        self._networkName = networkName
        self._coin = coin

        self._bitcoinabcRpcEndpoint = ""
        self._electrumCashRpcEndpoint = ""

    def loadConfig(self, config):
        self.bitcoinabcRpcEndpoint = config["bitcoinabcRpcEndpoint"]
        self.electrumCashRpcEndpoint = config["electrumCashRpcEndpoint"]

        return True, None

    @property
    def coin(self):
        return self._coin

    @property
    def networkName(self):
        return self._networkName

    @networkName.setter
    def networkName(self, value):
        self._networkName = value

    @property
    def bitcoinabcRpcEndpoint(self):
        return self._bitcoinabcRpcEndpoint

    @bitcoinabcRpcEndpoint.setter
    def bitcoinabcRpcEndpoint(self, value):
        self._bitcoinabcRpcEndpoint = value

    @property
    def electrumCashRpcEndpoint(self):
        return self._electrumCashRpcEndpoint

    @electrumCashRpcEndpoint.setter
    def electrumCashRpcEndpoint(self, value):
        self._electrumCashRpcEndpoint = value

    def jsonEncode(self):
        return ConfigEncoder().encode(self)


class ConfigEncoder(JSONEncoder):
    def encode(self, o):
        return {
            "bitcoinabcRpcEndpoint": o.bitcoinabcRpcEndpoint,
            "electrumCashRpcEndpoint": o.electrumCashRpcEndpoint
        }
