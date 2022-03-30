#!/usr/bin/python3
from json import JSONEncoder
from utils import utils


class Config:

    def __init__(self, coin, networkName):

        self._coin = coin
        self._networkName = networkName
        self._rpcProtocol = ""
        self._wsProtocol = ""
        self._host = ""
        self._rpcPort = ""
        self._wsPort = ""
        self._rpcEndpoint = ""
        self._wsEndpoint = ""

    def __attachNetworkToHost(self, host):
        return f"{host}-{self.networkName}"

    def __formDefaultUrl(self, protocol, host, port):
        return "{}://{}:{}".format(protocol, host, port)

    def loadConfig(self, config):

        defaultConfig, err = utils.loadDefaultPackageConf(self.coin)
        if err is not None:
            return False, err

        if "rpcEndpoint" in config:
            self.rpcEndpoint = config["rpcEndpoint"]
        else:
            self.rpcProtocol = defaultConfig["rpcProtocol"]
            self.host = self.__attachNetworkToHost(defaultConfig["host"])
            self.rpcPort = defaultConfig["rpcPort"]
            self.rpcEndpoint = self.__formDefaultUrl(self.rpcProtocol, self.host, self.rpcPort)

        if "wsEndpoint" in config:
            self.wsEndpoint = config["wsEndpoint"]
        else:
            self.wsProtocol = defaultConfig["wsProtocol"]
            self.wsPort = defaultConfig["wsPort"]
            self.wsEndpoint = self.__formDefaultUrl(self.wsProtocol, self.host, self.wsPort)

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
    def rpcProtocol(self):
        return self._rpcProtocol

    @rpcProtocol.setter
    def rpcProtocol(self, value):
        self._rpcProtocol = value

    @property
    def wsProtocol(self):
        return self._wsProtocol

    @wsProtocol.setter
    def wsProtocol(self, value):
        self._wsProtocol = value

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
    def wsPort(self):
        return self._wsPort

    @wsPort.setter
    def wsPort(self, value):
        self._wsPort = value

    @property
    def rpcEndpoint(self):
        return self._rpcEndpoint

    @rpcEndpoint.setter
    def rpcEndpoint(self, value):
        self._rpcEndpoint = value

    @property
    def wsEndpoint(self):
        return self._wsEndpoint

    @wsEndpoint.setter
    def wsEndpoint(self, value):
        self._wsEndpoint = value

    def jsonEncode(self):
        return ConfigEncoder().encode(self)


class ConfigEncoder(JSONEncoder):

    def encode(self, o):
        return {
            "rpcEndpoint": o.rpcEndpoint,
            "wsEndpoint": o.wsEndpoint
        }
