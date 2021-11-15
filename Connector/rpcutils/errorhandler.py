from .constants import *
from json import JSONEncoder


class Error(Exception):

    def __init__(self, message, code):
        self.message = message
        self.code = code
        super().__init__(self.message)

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
        super().__init__(message=message, code=INTERNAL_SERVER_ERROR_CODE)


class ErrorEncoder(JSONEncoder):

    def encode(self, o):
        return {
            CODE: o.code,
            MESSAGE: o.message
        }
