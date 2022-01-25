#!/usr/bin/python
from .constants import *
from json import JSONEncoder
from httputils import error


class RpcError(Exception):

    def __init__(self, id, message, code):
        self._message = message
        self._code = code
        self._id = id
        super().__init__(self.message)

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, value):
        self._code = value

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        self._message = value

    def parseToHttpError(self):
        return error.Error(
            message=self.message,
            code=self.code
        )

    def jsonEncode(self):
        return RpcErrorEncoder().encode(self)


class RpcBadRequestError(RpcError):

    def __init__(self, id, message):
        super().__init__(
            id=id,
            message=message,
            code=BAD_REQUEST_CODE
        )

    def parseToHttpError(self):
        return error.BadRequestError(message=self.message)


class RpcMethodNotAllowedError(RpcError):

    def __init__(self, id, message):
        super().__init__(
            id=id,
            message=message,
            code=METHOD_NOT_ALLOWED_CODE
        )

    def parseToHttpError(self):
        return error.MethodNotAllowedError(message=self.message)


class RpcInternalServerError(RpcError):

    def __init__(self, id, message):
        super().__init__(
            id=id,
            message=message,
            code=INTERNAL_SERVER_ERROR_CODE
        )

    def parseToHttpError(self):
        return error.InternalServerError(message=self.message)


class RpcNotFoundError(RpcError):

    def __init__(self, id, message):
        super().__init__(
            id=id,
            message=message,
            code=NOT_FOUND_CODE
        )

    def parseToHttpError(self):
        return error.NotFoundError(message=self.message)


class RpcErrorEncoder(JSONEncoder):

    def encode(self, o):
        return {
            ID: o.id,
            JSON_RPC: JSON_RPC_VERSION,
            ERROR: {
                CODE: o.code,
                MESSAGE: o.message
            }
        }
