#!/usr/bin/python
from .constants import *
from httputils import error as httpError
from json import JSONEncoder


class RpcError(Exception):

    def __init__(self, id: int, message: str, code: int):
        super().__init__(message)
        self._id = id
        self._code = code
        self._message = message

    @property
    def id(self):
        return self._id

    @property
    def code(self):
        return self._code

    @property
    def message(self):
        return self._message

    def parseToHttpError(self):
        return httpError.Error(message=self.message, code=self.code)

    def jsonEncode(self):
        return RpcErrorEncoder().encode(self)


class RpcBadRequestError(RpcError):

    def __init__(self, id: int, message: str = "Bad request"):
        super().__init__(id=id, message=message, code=BAD_REQUEST_CODE)

    def parseToHttpError(self):
        return httpError.BadRequestError(self.message)


class RpcMethodNotAllowedError(RpcError):

    def __init__(self, id: int, message: str = "Method not allowed"):
        super().__init__(id=id, message=message, code=METHOD_NOT_ALLOWED_CODE)

    def parseToHttpError(self):
        return httpError.MethodNotAllowedError(self.message)


class RpcInternalServerError(RpcError):

    def __init__(self, id: int, message: str = "Internal server error"):
        super().__init__(id=id, message=message, code=INTERNAL_SERVER_ERROR_CODE)

    def parseToHttpError(self):
        return httpError.InternalServerError(self.message)


class RpcNotFoundError(RpcError):

    def __init__(self, id: int, message: str = "Not found"):
        super().__init__(id=id, message=message, code=NOT_FOUND_CODE)

    def parseToHttpError(self):
        return httpError.NotFoundError(self.message)


class RpcBadGatewayError(RpcError):

    def __init__(self, id: int, message: str = "Bad gateway"):
        super().__init__(id=id, message=message, code=BAD_GATEWAY_CODE)

    def parseToHttpError(self):
        return httpError.BadGatewayError(self.message)


class RpcErrorEncoder(JSONEncoder):

    def encode(self, o):
        return {
            "id": o.id,
            "jsonrpc": JSON_RPC_VERSION,
            "error": {
                "message": o.message,
                "code": o.code
            }
        }
