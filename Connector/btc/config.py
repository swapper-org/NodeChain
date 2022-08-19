#!/usr/bin/python3
from json import JSONEncoder


class Config:

    def __init__(self, coin, networkName):

        self._coin = coin
        self._networkName = networkName

        self._bitcoincoreRpcEndpoint = ""
        self._electrumRpcEndpoint = ""
        self._bitcoincoreZmqEndpoint = ""
        self._bitcoinAddressCallbackHost = ""
        self._electrsEndpoint = ""

    def loadConfig(self, config):

        try:
            self.bitcoincoreRpcEndpoint = config["bitcoincoreRpcEndpoint"]
            self.bitcoincoreZmqEndpoint = config["bitcoincoreZmqEndpoint"]
            self.bitcoinAddressCallbackHost = config["bitcoinAddressCallbackHost"]
            self.electrsEndpoint = config["electrsEndpoint"]
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
    def bitcoincoreRpcEndpoint(self):
        return self._bitcoincoreRpcEndpoint

    @bitcoincoreRpcEndpoint.setter
    def bitcoincoreRpcEndpoint(self, value):
        self._bitcoincoreRpcEndpoint = value

    @property
    def bitcoincoreZmqEndpoint(self):
        return self._bitcoincoreZmqEndpoint

    @bitcoincoreZmqEndpoint.setter
    def bitcoincoreZmqEndpoint(self, value):
        self._bitcoincoreZmqEndpoint = value

    @property
    def bitcoinAddressCallbackHost(self):
        return self._bitcoinAddressCallbackHost

    @bitcoinAddressCallbackHost.setter
    def bitcoinAddressCallbackHost(self, value):
        self._bitcoinAddressCallbackHost = value

    @property
    def electrsEndpoint(self):
        return self._electrsEndpoint

    @electrsEndpoint.setter
    def electrsEndpoint(self, value):
        self._electrsEndpoint = value

    def jsonEncode(self):
        return ConfigEncoder().encode(self)


class ConfigEncoder(JSONEncoder):
    def encode(self, o):
        return {
            "bitcoincoreRpcEndpoint": o.bitcoincoreRpcEndpoint,
            "bitcoincoreZmqEndpoint": o.bitcoincoreZmqEndpoint,
            "bitcoinAddressCallbackHost": o.bitcoinAddressCallbackHost,
            "electrsEndpoint": o.electrsEndpoint
        }
