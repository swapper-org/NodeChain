#!/usr/bin/python3
from json import JSONEncoder


class Config:
    def __init__(self, coin, networkName):

        self._networkName = networkName
        self._coin = coin

        self._terradRpcEndpoint = ""

    def loadConfig(self, config):
        self.terradRpcEndpoint = config["terradRpcEndpoint"]

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
    def terradRpcEndpoint(self):
        return self._terradRpcEndpoint

    @terradRpcEndpoint.setter
    def terradRpcEndpoint(self, value):
        self._terradRpcEndpoint = value

    def jsonEncode(self):
        return ConfigEncoder().encode(self)


class ConfigEncoder(JSONEncoder):
    def encode(self, o):
        return {
            "terradRpcEndpoint": o.terradRpcEndpoint
        }
