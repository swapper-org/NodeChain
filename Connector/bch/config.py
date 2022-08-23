#!/usr/bin/python3
from json import JSONEncoder


class Config:

    def __init__(self, coin, networkName):

        self._networkName = networkName
        self._coin = coin

        self._bitcoinabcRpcEndpoint = ""
        self._electronCashRpcEndpoint = ""

    def loadConfig(self, config):

        try:
            self.bitcoinabcRpcEndpoint = config["bitcoinabcRpcEndpoint"]
            self.electronCashRpcEndpoint = config["electronCashRpcEndpoint"]
        except KeyError:
            return False, "Can not load config"

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
    def electronCashRpcEndpoint(self):
        return self._electronCashRpcEndpoint

    @electronCashRpcEndpoint.setter
    def electronCashRpcEndpoint(self, value):
        self._electronCashRpcEndpoint = value

    def jsonEncode(self):
        return ConfigEncoder().encode(self)


class ConfigEncoder(JSONEncoder):
    def encode(self, o):
        return {
            "bitcoinabcRpcEndpoint": o.bitcoinabcRpcEndpoint,
            "electronCashRpcEndpoint": o.electronCashRpcEndpoint
        }
