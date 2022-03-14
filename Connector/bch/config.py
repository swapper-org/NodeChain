#!/usr/bin/python3
from json import JSONEncoder
from utils import utils


class Config:

    def __init__(self, coin, networkName):

        self._networkName = networkName
        self._coin = coin
        self._bitcoinabcProtocol = ""
        self._bitcoinabcHost = ""
        self._bitcoinabcPort = ""
        self._bitcoinabcUser = ""
        self._bitcoinabcPassword = ""
        self._electrumCashProtocol = ""
        self._electrumCashHost = ""
        self._electrumCashPort = ""
        self._electrumCashUser = ""
        self._electrumCashPassword = ""

    def __attachNetworkToHost(self, host):
        return f"{host}-{self.networkName}"

    def loadConfig(self, config):

        defaultConfig, err = utils.loadDefaultPackageConf(self.coin)
        if err is not None:
            return False, err

        self.bitcoinabcProtocol = config["bitcoinabcProtocol"] if "bitcoinabcProtocol" in config \
            else defaultConfig["bitcoinabcProtocol"]
        self.bitcoinabcHost = config["bitcoinabcHost"] if "bitcoinabcHost" in config \
            else self.__attachNetworkToHost(defaultConfig["bitcoinabcHost"])

        if "bitcoinabcPort" in config:
            if config["bitcoinabcPort"].isdigit():
                self.bitcoinabcPort = config["bitcoinabcPort"]
            else:
                return False, f"Value {config['bitcoinabcPort']} for bitcoinabcPort is not digit"
        else:
            self.bitcoinabcPort = defaultConfig["bitcoinabcPort"]

        self.bitcoinabcUser = config["bitcoinabcUser"] if "bitcoinabcUser" in config \
            else defaultConfig["bitcoinabcUser"]
        self.bitcoinabcPassword = config["bitcoinabcPassword"] if "bitcoinabcPassword" in config \
            else defaultConfig["bitcoinabcPassword"]
        self.electrumCashProtocol = config["electrumCashProtocol"] if "electrumCashProtocol" in config \
            else defaultConfig["electrumCashProtocol"]
        self.electrumCashHost = config["electrumCashHost"] if "electrumCashHost" in config \
            else self.__attachNetworkToHost(defaultConfig["electrumCashHost"])

        if "electrumCashPort" in config:
            if config["electrumCashPort"].isdigit():
                self.electrumCashPort = config["electrumCashPort"]
            else:
                return False, f"Value {config['electrumCashPort']} for electrumCashPort is not digit"
        else:
            self.electrumCashPort = defaultConfig["electrumCashPort"]

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
    def bitcoinabcProtocol(self):
        return self._bitcoinabcProtocol

    @bitcoinabcProtocol.setter
    def bitcoinabcProtocol(self, value):
        self._bitcoinabcProtocol = value

    @property
    def bitcoinabcHost(self):
        return self._bitcoinabcHost

    @bitcoinabcHost.setter
    def bitcoinabcHost(self, value):
        self._bitcoinabcHost = value

    @property
    def bitcoinabcPort(self):
        return self._bitcoinabcPort

    @bitcoinabcPort.setter
    def bitcoinabcPort(self, value):
        self._bitcoinabcPort = value

    @property
    def bitcoinabcUser(self):
        return self._bitcoinabcUser

    @bitcoinabcUser.setter
    def bitcoinabcUser(self, value):
        self._bitcoinabcUser = value

    @property
    def bitcoinabcPassword(self):
        return self._bitcoinabcPassword

    @bitcoinabcPassword.setter
    def bitcoinabcPassword(self, value):
        self._bitcoinabcPassword = value

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
    def bitcoinabcRpcEndpoint(self):
        return f"{self.bitcoinabcProtocol}://" \
               f"{self.bitcoinabcUser}:{self.bitcoinabcPassword}@" \
               f"{self.bitcoinabcHost}:{self.bitcoinabcPort}"

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
            "bitcoinabcProtocol": o.bitcoinabcProtocol,
            "bitcoinabcHost": o.bitcoinabcHost,
            "bitcoinabcPort": o.bitcoinabcPort,
            "bitcoinabcUser": o.bitcoinabcUser,
            "bitcoinabcPassword": o.bitcoinabcPassword,
            "electrumCashProtocol": o.electrumCashProtocol,
            "electrumCashHost": o.electrumCashHost,
            "electrumCashPort": o.electrumCashPort,
            "electrumCashUser": o.electrumCashUser,
            "electrumCashPassword": o.electrumCashPassword
        }
