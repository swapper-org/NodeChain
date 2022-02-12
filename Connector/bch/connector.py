#!/usr/bin/python3
from json import JSONEncoder


class Config:

    def __init__(self, networkName, config):

        # TODO: Load here default config to avoid code reps

        self._networkName = networkName
        self._bitcoincoreProtocol = config["bitcoincoreProtocol"]
        self._bitcoincoreHost = config["bitcoincoreHost"]
        self._bitcoincorePort = config["bitcoincorePort"]
        self._bitcoincoreUser = config["bitcoincoreUser"]
        self._bitcoincorePassword = config["bitcoincorePassword"]
        self._electrumCashProtocol = config["electrumCashProtocol"]
        self._electrumCashHost = config["electrumCashHost"]
        self._electrumCashPort = config["electrumCashPort"]
        self._electrumCashUser = config["electrumCashUser"]
        self._electrumCashPassword = config["electrumCashPassword"]

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
    def electrumCashProtocol(self):
        return self._electrumCashProtocol

    @electrumCashProtocol.setter
    def electrumCashProtocol(self, value):
        self._electrumCashProtocol = value

    @property
    def electrumCashHost(self):
        return self._electrumCashHost

    @electrumCashHost.setter
    def electrumCashHost(self, value):
        self._electrumCashHost = value

    @property
    def electrumCashPort(self):
        return self._electrumCashPort

    @electrumCashPort.setter
    def electrumCashPort(self, value):
        self.electrumCashPort = value

    @property
    def electrumCashUser(self):
        return self._electrumCashUser

    @electrumCashUser.setter
    def electrumCashUser(self, value):
        self._electrumCashUser = value

    @property
    def electrumCashPassword(self):
        return self._electrumCashPassword

    @electrumCashPassword.setter
    def electrumCashPassword(self, value):
        self._electrumCashPassword = value

    @property
    def bitcoincoreRpcEndpoint(self):
        return f"{self.bitcoincoreProtocol}://" \
               f"{self.bitcoincoreUser}:{self.bitcoincorePassword}@" \
               f"{self.bitcoincoreHost}:{self.bitcoincorePort}"

    @property
    def electrumCashRpcEndpoint(self):
        return f"{self.electrumCashProtocol}://" \
               f"{self.electrumCashUser}:{self.electrumCashPassword}@" \
               f"{self.electrumCashHost}:{self.electrumCashPort}"

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
            "electrumCashProtocol": o.electrumCashProtocol,
            "electrumCashHost": o.electrumCashHost,
            "electrumCashPort": o.electrumCashPort,
            "electrumCashUser": o.electrumCashUser,
            "electrumCashPassword": o.electrumCashPassword
        }
