#!/usr/bin/python3
from json import JSONEncoder
from utils import utils


class Config:

    def __init__(self, coin, networkName):

        self._coin = coin
        self._networkName = networkName
        self._protocol = ""
        self._host = ""
        self._rpcPort = ""
        self._wsPort = ""

    def loadConfig(self, config):

        defaultConfig, err = utils.loadDefaultPackageConf(self.coin)
        if err is not None:
            return False, err

        self.protocol = config["protocol"] if "protocol" in config else defaultConfig["protocol"]
        self.host = config["host"] if "host" in config else defaultConfig["host"]

        if "rpcPort" in config:
            if config["rpcPort"].isdigit():
                self.rpcPort = config["rpcPort"]
            else:
                return False, f"Value {config['rpcPort']} for rpcPort is not digit"
        else:
            self.rpcPort = defaultConfig["rpcPort"]

        if "wsPort" in config:
            if config["wsPort"].isdigit():
                self.wsPort = config["wsPort"]
            else:
                return False, f"Value {config['wsPort']} for wsPort is not digit"
        else:
            self.wsPort = defaultConfig["wsPort"]

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
    def wsPort(self):
        return self._wsPort

    @wsPort.setter
    def wsPort(self, value):
        self._wsPort = value

    @property
    def rpcEndpoint(self):
        return "{}://{}:{}".format(self.protocol, self.host, self.rpcPort)

    @property
    def wsEndpoint(self):
        return "{}://{}:{}".format(self.protocol, self.host, self.wsPort)

    def jsonEncode(self):
        return ConfigEncoder().encode(self)


class ConfigEncoder(JSONEncoder):

    def encode(self, o):
        return {
            "protocol": o.protocol,
            "host": o.host,
            "rpcPort": o.rpcPort,
            "wsPort": o.wsPort
        }
