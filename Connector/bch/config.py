#!/usr/bin/python3
from json import JSONEncoder
from utils import utils


class Config:

    def __init__(self, coin, networkName):

        self._networkName = networkName
        self._coin = coin
        self._bitcoincoreProtocol = ""
        self._bitcoincoreHost = ""
        self._bitcoincorePort = ""
        self._bitcoincoreUser = ""
        self._bitcoincorePassword = ""
        self._electrumCashProtocol = ""
        self._electrumCashHost = ""
        self._electrumCashPort = ""
        self._electrumCashUser = ""
        self._electrumCashPassword = ""

    def loadConfig(self, config):

        defaultConfig, err = utils.loadDefaultPackageConf(self.coin)
        if err is not None:
            return False, err

        self.bitcoincoreProtocol = config["bitcoincoreProtocol"] if "bitcoincoreProtocol" in config \
            else defaultConfig["bitcoincoreProtocol"]
        self.bitcoincoreHost = config["bitcoincoreHost"] if "bitcoincoreHost" in config \
            else defaultConfig["bitcoincoreHost"]
        self.bitcoincorePort = config["bitcoincorePort"] if "bitcoincorePort" in config \
            else defaultConfig["bitcoincorePort"]
        self.bitcoincoreUser = config["bitcoincoreUser"] if "bitcoincoreUser" in config \
            else defaultConfig["bitcoincoreUser"]
        self.bitcoincorePassword = config["bitcoincorePassword"] if "bitcoincorePassword" in config \
            else defaultConfig["bitcoincorePassword"]
        self.electrumCashProtocol = config["electrumCashProtocol"] if "electrumCashProtocol" in config \
            else defaultConfig["electrumCashProtocol"]
        self.electrumCashHost = config["electrumCashHost"] if "electrumCashHost" in config \
            else defaultConfig["electrumCashHost"]
        self.electrumCashPort = config["electrumCashPort"] if "electrumCashPort" in config \
            else defaultConfig["electrumCashPort"]
        self.electrumCashUser = config["electrumCashUser"] if "electrumCashUser" in config \
            else defaultConfig["electrumCashUser"]
        self.electrumCashPassword = config["electrumCashPassword"] if "electrumCashPassword" in config \
            else defaultConfig["electrumCashPassword"]

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
        self._electrumCashPort = value

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
