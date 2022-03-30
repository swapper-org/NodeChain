#!/usr/bin/python
from json import JSONEncoder


class Config:

    def __init__(self, coin, networkName):

        self._coin = coin
        self._networkName = networkName

        self._monerodRpcEndpoint = ""

    def loadConfig(self, config):
        self.monerodRpcEndpoint = ["monerodRpcEndpoint"]

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
    def monerodRpcEndpoint(self):
        return self._monerodRpcEndpoint

    @monerodRpcEndpoint.setter
    def monerodRpcEndpoint(self, value):
        self._monerodRpcEndpoint = value

    def jsonEncode(self):
        return ConfigEncoder().encode(self)


class ConfigEncoder(JSONEncoder):

    def encode(self, o):
        return {
            "monerodRpcEndpoint": o.monerodRpcEndpoint
        }
