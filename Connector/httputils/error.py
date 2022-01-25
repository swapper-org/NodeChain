#!/usr/bin/python
from .constants import *
from json import JSONEncoder


class Error(Exception):

    def __init__(self, message, code):
        self.message = message
        self.code = code
        super().__init__(self.message)

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, value):
        self._code = value

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        self._message = value

    def jsonEncode(self):
        return ErrorEncoder().encode(self)


class BadRequestError(Error):

    def __init__(self, message):
        super().__init__(message=message, code=BAD_REQUEST_CODE)


class MethodNotAllowedError(Error):

    def __init__(self, message):
        super().__init__(message=message, code=METHOD_NOT_ALLOWED_CODE)


class InternalServerError(Error):

    def __init__(self, message):
        super().__init__(message=message, code=INTERNAL_SERVER_ERROR_CODE)


class NotFoundError(Error):

    def __init__(self, message):
        super().__init__(message=message, code=NOT_FOUND_CODE)


class ConflictError(Error):

    def __init__(self, message):
        super().__init__(message=message, code=CONFLICT_ERROR_CODE)


class ErrorEncoder(JSONEncoder):

    def encode(self, o):
        return {
            "message": o.message,
            "code": o.code
        }
