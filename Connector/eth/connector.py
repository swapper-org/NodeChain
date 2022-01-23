#!/usr/bin/python3
from json import JSONEncoder


class Config:

    def __init__(self, config):

        self._protocol = config["protocol"]
        self._host = config["host"]
        self._rpcPort = config["rpcPort"]
        self._wsPort = config["wsPort"]

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
        return ErrorEncoder().encode(self)


class ErrorEncoder(JSONEncoder):

    def encode(self, o):
        return {
            "protocol": o.protocol,
            "host": o.host,
            "rpcPort": o.rpcPort,
            "wsPort": o.wsPort
        }
