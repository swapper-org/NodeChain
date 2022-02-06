#!/usr/bin/python3
from json import JSONEncoder

BITCOIN_CALLBACK_PATH = "/bitcoincallback"
BITCOIN_CALLBACK_ENDPOINT = "http://{}:{}{}".format("connector", 80, BITCOIN_CALLBACK_PATH)
ELECTRUM_NAME = "electrum"


class Config:

    def __init__(self, networkName, config):
        self._networkName = networkName
        self._bitcoincoreProtocol = config["bitcoincoreProtocol"]
        self._bitcoincoreHost = config["bitcoincoreHost"]
        self._bitcoincorePort = config["bitcoincorePort"]
        self._bitcoincoreUser = config["bitcoincoreUser"]
        self._bitcoincorePassword = config["bitcoincorePassword"]
        self._bitcoincoreZmqProtocol = config["bitcoincoreZmqProtocol"]
        self._bitcoincoreZmqPort = config["bitcoincoreZmqPort"]
        self._electrumProtocol = config["electrumProtocol"]
        self._electrumHost = config["electrumHost"]
        self._electrumPort = config["electrumPort"]
        self._electrumUser = config["electrumUser"]
        self._electrumPassword = config["electrumPassword"]

    @property
    def networkName(self):
        return self._networkName

    @networkName.setter
    def networkName(self, value):
        self._networkName = value

    @property
    def bitcoincoreProtocol(self):
        return self._bitcoincoreProtocol

    @bitcoincoreProtocol.setter
    def bitcoincoreProtocol(self, value):
        self._bitcoincoreProtocol = value

    @property
    def bitcoincoreHost(self):
        return self._bitcoincoreHost

    @bitcoincoreHost.setter
    def bitcoincoreHost(self, value):
        self._bitcoincoreHost = value

    @property
    def bitcoincorePort(self):
        return self._bitcoincorePort

    @bitcoincorePort.setter
    def bitcoincorePort(self, value):
        self._bitcoincorePort = value

    @property
    def bitcoincoreUser(self):
        return self._bitcoincoreUser

    @bitcoincoreUser.setter
    def bitcoincoreUser(self, value):
        self._bitcoincoreUser = value

    @property
    def bitcoincorePassword(self):
        return self._bitcoincorePassword

    @bitcoincorePassword.setter
    def bitcoincorePassword(self, value):
        self._bitcoincorePassword = value

    @property
    def bitcoincoreZmqProtocol(self):
        return self._bitcoincoreZmqProtocol

    @bitcoincoreZmqProtocol.setter
    def bitcoincoreZmqProtocol(self, value):
        self._bitcoincoreZmqProtocol = value

    @property
    def bitcoincoreZmqPort(self):
        return self._bitcoincoreZmqPort

    @bitcoincoreZmqPort.setter
    def bitcoincoreZmqPort(self, value):
        self._bitcoincoreZmqPort = value

    @property
    def electrumProtocol(self):
        return self._electrumProtocol

    @electrumProtocol.setter
    def electrumProtocol(self, value):
        self._electrumProtocol = value

    @property
    def electrumHost(self):
        return self._electrumHost

    @electrumHost.setter
    def electrumHost(self, value):
        self._electrumHost = value

    @property
    def electrumPort(self):
        return self._electrumPort

    @electrumPort.setter
    def electrumPort(self, value):
        self.electrumPort = value

    @property
    def electrumUser(self):
        return self._electrumUser

    @electrumUser.setter
    def electrumUser(self, value):
        self._electrumUser = value

    @property
    def electrumPassword(self):
        return self._electrumPassword

    @electrumPassword.setter
    def electrumPassword(self, value):
        self._electrumPassword = value

    @property
    def bitcoincoreRpcEndpoint(self):
        return f"{self.bitcoincoreProtocol}://" \
               f"{self.bitcoincoreUser}:{self.bitcoincorePassword}@" \
               f"{self.bitcoincoreHost}:{self.bitcoincorePort}"

    @property
    def electrumRpcEndpoint(self):
        return f"{self.electrumProtocol}://" \
               f"{self.electrumUser}:{self.electrumPassword}@" \
               f"{self.electrumHost}:{self.electrumPort}"

    @property
    def bitcoincoreZmqEndpoint(self):
        return f"{self.bitcoincoreZmqProtocol}://" \
               f"{self.bitcoincoreHost}:{self.bitcoincorePort}"

    def jsonEncode(self):
        return ConfigEncoder().encode(self)


class ConfigEncoder(JSONEncoder):
    def encode(self, o):
        return {
            "bitcoincoreProtocol": o.bitcoincoreProtocol,
            "bitcoincoreHost": o.bitcoincoreHost,
            "bitcoincorePort": o.bitcoincorePort,
            "bitcoincoreUser": o.bitcoincoreUser,
            "bitcoincorePassword": o.bitcoincorePassword,
            "bitcoincoreZmqProtocol": o.bitcoincoreZmqProtocol,
            "bitcoincoreZmqPort": o.bitcoincoreZmqPort,
            "electrumProtocol": o.electrumProtocol,
            "electrumHost": o.electrumHost,
            "electrumPort": o.electrumPort,
            "electrumUser": o.electrumUser,
            "electrumPassword": o.electrumPassword
        }
