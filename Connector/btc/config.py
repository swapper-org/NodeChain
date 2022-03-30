#!/usr/bin/python3
from json import JSONEncoder
from utils import utils


class Config:

    def __init__(self, coin, networkName):

        self._coin = coin
        self._networkName = networkName

        self._bitcoincoreProtocol = ""
        self._bitcoincoreHost = ""
        self._bitcoincorePort = ""
        self._bitcoincoreUser = ""
        self._bitcoincorePassword = ""
        self._bitcoincoreZmqProtocol = ""
        self._bitcoincoreZmqPort = ""
        self._electrumProtocol = ""
        self._electrumHost = ""
        self._electrumPort = ""
        self._electrumUser = ""
        self._electrumPassword = ""
        self._bitcoincoreCallbackProtocol = ""
        self._bitcoincoreCallbackHost = ""
        self._bitcoincoreCallbackPort = ""
        self._electrumxHost = ""
        self._electrumxPort = ""
        self._bitcoincoreRpcEndpoint = ""
        self._electrumRpcEndpoint = ""
        self._bitcoincoreZmqEndpoint = ""
        self._bitcoinAddressCallbackHost = ""

    def __attachNetworkToHost(self, host):
        return f"{host}-{self.networkName}"

    def __formDefaultUrl(self, protocol, host, port, user=None, passwd=None):
        if not user and not passwd:
            return "{}://{}:{}".format(protocol, host, port)
        else:
            return "{}://{}:{}@{}:{}".format(protocol, user, passwd, host, port)

    def loadConfig(self, config):

        defaultConfig, err = utils.loadDefaultPackageConf(self.coin)
        if err is not None:
            return False, err

        if "bitcoincoreRpcEndpoint" in config:
            self.bitcoincoreRpcEndpoint = config["bitcoincoreRpcEndpoint"]
        else:
            self.bitcoincoreProtocol = defaultConfig["bitcoincoreProtocol"]
            self.bitcoincoreHost = self.__attachNetworkToHost(defaultConfig["bitcoincoreHost"])
            self.bitcoincorePort = defaultConfig["bitcoincorePort"]
            self.bitcoincoreUser = defaultConfig["bitcoincoreUser"]
            self.bitcoincorePassword = defaultConfig["bitcoincorePassword"]
            self.bitcoincoreRpcEndpoint = self.__formDefaultUrl(self.bitcoincoreProtocol, self.bitcoincoreHost, self.bitcoincorePort, self.bitcoincoreUser, self.bitcoincorePassword)

        if "bitcoincoreZmqEndpoint" in config:
            self.bitcoincoreZmqEndpoint = config["bitcoincoreZmqEndpoint"]
        else:
            self.bitcoincoreZmqProtocol = defaultConfig["bitcoincoreZmqProtocol"]
            self.bitcoincoreZmqPort = defaultConfig["bitcoincoreZmqPort"]
            self.bitcoincoreZmqEndpoint = self.__formDefaultUrl(self.bitcoincoreZmqProtocol, self.bitcoincoreHost, self.bitcoincoreZmqPort)

        if "electrumRpcEndpoint" in config:
            self.electrumRpcEndpoint = config["electrumRpcEndpoint"]
        else:
            self.electrumProtocol = defaultConfig["electrumProtocol"]
            self.electrumHost = self.__attachNetworkToHost(defaultConfig["electrumHost"])
            self.electrumPort = defaultConfig["electrumPort"]
            self.electrumUser = defaultConfig["electrumUser"]
            self.electrumPassword = defaultConfig["electrumPassword"]
            self.electrumRpcEndpoint = self.__formDefaultUrl(self.electrumProtocol, self.electrumHost, self.electrumPort, self.electrumUser, self.electrumPassword)

        if "bitcoinAddressCallbackHost" in config:
            self.bitcoinAddressCallbackHost = config["bitcoinAddressCallbackHost"]
        else:
            self.bitcoincoreCallbackProtocol = defaultConfig["bitcoincoreCallbackProtocol"]
            self.bitcoincoreCallbackHost = defaultConfig["bitcoincoreCallbackHost"]
            self.bitcoincoreCallbackPort = defaultConfig["bitcoincoreCallbackPort"]
            self.bitcoinAddressCallbackHost = self.__formDefaultUrl(self.bitcoincoreCallbackProtocol, self.bitcoincoreCallbackHost, self.bitcoincoreCallbackPort)

        # TODO: This may be removed in the future
        self.electrumxHost = config["electrumxHost"] if "electrumxHost" in config \
            else self.__attachNetworkToHost(defaultConfig["electrumxHost"])

        if "electrumxPort" in config:
            if config["electrumxPort"].isdigit():
                self.electrumxPort = config["electrumxPort"]
            else:
                return False, f"Value {config['electrumxPort']} for electrumxPort is not digit"
        else:
            self.electrumxPort = defaultConfig["electrumxPort"]

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
        self._electrumPort = value

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
    def bitcoincoreCallbackProtocol(self):
        return self._bitcoincoreCallbackProtocol

    @bitcoincoreCallbackProtocol.setter
    def bitcoincoreCallbackProtocol(self, value):
        self._bitcoincoreCallbackProtocol = value

    @property
    def bitcoincoreCallbackHost(self):
        return self._bitcoincoreCallbackHost

    @bitcoincoreCallbackHost.setter
    def bitcoincoreCallbackHost(self, value):
        self._bitcoincoreCallbackHost = value

    @property
    def bitcoincoreCallbackPort(self):
        return self._bitcoincoreCallbackPort

    @bitcoincoreCallbackPort.setter
    def bitcoincoreCallbackPort(self, value):
        self._bitcoincoreCallbackPort = value

    # TODO: This may be removed in the future
    @property
    def electrumxHost(self):
        return self._electrumxHost

    @electrumxHost.setter
    def electrumxHost(self, value):
        self._electrumxHost = value

    @property
    def electrumxPort(self):
        return self._electrumxPort

    @electrumxPort.setter
    def electrumxPort(self, value):
        self._electrumxPort = value

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
            "bitcoincoreCallbackProtocol": o.bitcoincoreCallbackProtocol,
            "bitcoincoreCallbackHost": o.bitcoincoreCallbackHost,
            "electrumProtocol": o.electrumProtocol,
            "electrumHost": o.electrumHost,
            "electrumPort": o.electrumPort,
            "electrumUser": o.electrumUser,
            "electrumPassword": o.electrumPassword,
            "electrumxHost": o.electrumxHost,
            "electrumxPort": o.electrumxPort,
            "bitcoincoreRpcEndpoint": o.bitcoincoreRpcEndpoint,
            "electrumRpcEndpoint": o.electrumRpcEndpoint,
            "bitcoincoreZmqEndpoint": o.bitcoincoreZmqEndpoint,
            "bitcoinAddressCallbackHost": o.bitcoinAddressCallbackHost
        }
