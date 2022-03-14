#!/usr/bin/python
from json import JSONEncoder
from utils import utils


class Config:

    def __init__(self, coin, networkName):

        self._coin = coin
        self._networkName = networkName
        self._protocol = ""
        self._host = ""
        self._rpcPort = 0
        self._rpcPath = ""

    def __attachNetworkToHost(self, host):
        return f"{host}-{self.networkName}"

    def loadConfig(self, config):

        defaultConfig, err = utils.loadDefaultPackageConf(self.coin)
        if err is not None:
            return False, err

        self.protocol = config["protocol"] if "protocol" in config else defaultConfig["protocol"]
        self.host = config["host"] if "host" in config else self.__attachNetworkToHost(defaultConfig["host"])
        self.rpcPort = config["rpcPort"] if "rpcPort" in config else defaultConfig["rpcPort"]
        self.rpcPath = config["rpcPath"] if "rpcPath" in config else defaultConfig["rpcPath"]

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
    def protocol(self):
        return self._protocol

    @protocol.setter
    def protocol(self, value):
        self._protocol = value

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        self._host = value

    @property
    def rpcPort(self):
        return self._rpcPort

    @rpcPort.setter
    def rpcPort(self, value):
        self._rpcPort = value

    @property
    def rpcPath(self):
        return self._rpcPath

    @rpcPath.setter
    def rpcPath(self, value):
        self._rpcPath = value

    @property
    def rpcEndpoint(self):
        return f"{self.protocol}://{self.host}:{self.rpcPort}/{self.rpcPath}"

    def jsonEncode(self):
        return ConfigEncoder().encode(self)


class ConfigEncoder(JSONEncoder):

    def encode(self, o):
        return {
            "protocol": o.protocol,
            "host": o.host,
            "rpcPort": o.rpcPort,
            "rpcPath": o.rpcPath
        }
