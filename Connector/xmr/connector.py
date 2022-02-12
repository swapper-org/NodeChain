#!/usr/bin/python


class Config:

    def __init__(self, networkName, config):

        self._networkName = networkName
        self._protocol = config["protocol"]
        self._host = config["host"]
        self._rpcPort = config["rpcPort"]
        self._rpcPath = config["rpcPath"]

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
