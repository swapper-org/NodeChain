#!/usr/bin/python3
from json import JSONEncoder
from utils import utils


class Config:

    def __init__(self, coin, networkName):

        self._networkName = networkName
        self._coin = coin
        self._terradProtocol = ""
        self._terradHost = ""
        self._terradPort = 0

    def loadConfig(self, config):

        defaultConfig, err = utils.loadDefaultPackageConf(self.coin)
        if err is not None:
            return False, err

        self.terradProtocol = config["terradProtocol"] if "terradProtocol" in config \
            else defaultConfig["terradProtocol"]
        self.terradHost = config["terradHost"] if "terradHost" in config \
            else defaultConfig["terradHost"]
        self.terradPort = config["terradPort"] if "terradPort" in config \
            else defaultConfig["terradPort"]

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
    def terradProtocol(self):
        return self._terradProtocol

    @terradProtocol.setter
    def terradProtocol(self, value):
        self._terradProtocol = value

    @property
    def terradHost(self):
        return self._terradHost

    @terradHost.setter
    def terradHost(self, value):
        self._terradHost = value

    @property
    def terradPort(self):
        return self._terradPort

    @terradPort.setter
    def terradPort(self, value):
        self._terradPort = value

    @property
    def terradRpcEndpoint(self):
        return f"{self.terradProtocol}://" \
               f"{self.terradHost}:{self.terradPort}"

    def jsonEncode(self):
        return ConfigEncoder().encode(self)


class ConfigEncoder(JSONEncoder):
    def encode(self, o):
        return {
            "terradProtocol": o.terradProtocol,
            "terradHost": o.terradHost,
            "terradPort": o.terradPort
        }
