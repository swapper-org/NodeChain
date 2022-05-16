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
        self._electrsHost = ""
        self._electrsPort = ""

    def loadConfig(self, config):
        self.bitcoincoreRpcEndpoint = config["bitcoincoreRpcEndpoint"]
        self.electrumRpcEndpoint = config["electrumRpcEndpoint"]
        self.bitcoincoreZmqEndpoint = config["bitcoincoreZmqEndpoint"]
        self.bitcoinAddressCallbackHost = config["bitcoinAddressCallbackHost"]
        self.electrsHost = config["electrsHost"]
        self.electrsPort = config["electrsPort"]

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
    def electrumRpcEndpoint(self):
        return self._electrumRpcEndpoint

    @electrumRpcEndpoint.setter
    def electrumRpcEndpoint(self, value):
        self._electrumRpcEndpoint = value

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
    def electrsHost(self):
        return self._electrsHost

    @electrsHost.setter
    def electrsHost(self, value):
        self._electrsHost = value
        
    @property
    def electrsPort(self):
        return self._electrsPort

    @electrsPort.setter
    def electrsPort(self, value):
        self._electrsPort = value

    def jsonEncode(self):
        return ConfigEncoder().encode(self)


class ConfigEncoder(JSONEncoder):
    def encode(self, o):
        return {
            "bitcoincoreRpcEndpoint": o.bitcoincoreRpcEndpoint,
            "electrumRpcEndpoint": o.electrumRpcEndpoint,
            "bitcoincoreZmqEndpoint": o.bitcoincoreZmqEndpoint,
            "bitcoinAddressCallbackHost": o.bitcoinAddressCallbackHost,
            "electrsHost": o.electrsHost,
            "electrsPort": o.electrsPort
        }
