#!/usr/bin/python
from .constants import *
from json import JSONEncoder


class Error(Exception):

    def __init__(self, message: str, code: int):
        super().__init__(message)
        self._message = message
        self._code = code

    @property
    def code(self):
        return self._code

    @property
    def message(self):
        return self._message

    def jsonEncode(self):
        return ErrorEncoder().encode(self)


class BadRequestError(Error):

    def __init__(self, message: str = "Bad request"):
        super().__init__(message=message, code=BAD_REQUEST_CODE)


class MethodNotAllowedError(Error):

    def __init__(self, message: str = "Method not allowed"):
        super().__init__(message=message, code=METHOD_NOT_ALLOWED_CODE)


class InternalServerError(Error):

    def __init__(self, message: str = "Internal server error"):
        super().__init__(message=message, code=INTERNAL_SERVER_ERROR_CODE)


class NotFoundError(Error):

    def __init__(self, message: str = "Not found"):
        super().__init__(message=message, code=NOT_FOUND_CODE)


class TimeoutError(Error):

    def __init__(self, message: str = "Timeout"):
        super().__init__(message=message, code=TIME_OUT_CODE)


class ConflictError(Error):

    def __init__(self, message: str = "Conflict error"):
        super().__init__(message=message, code=CONFLICT_ERROR_CODE)


class UnauthorizedError(Error):

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message=message, code=UNAUTHORIZED_ERROR_CODE)


class BadGatewayError(Error):

    def __init__(self, message: str = "Bad gateway"):
        super().__init__(message=message, code=BAD_GATEWAY_CODE)


class ErrorEncoder(JSONEncoder):

    def encode(self, o):
        return {
            "message": o.message,
            "code": o.code
        }
