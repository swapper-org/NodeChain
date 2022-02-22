#!/usr/bin/python
import requests
from logger import logger
from . import error
from .constants import *


class RPCConnector():

    @staticmethod
    def request(endpoint, id, method, params):

        try:

            payload = {
                ID: id,
                METHOD: method,
                PARAMS: params,
                JSON_RPC: JSON_RPC_VERSION
            }

            logger.printInfo(f"Making RPC Request to {endpoint}. Payload: {payload}")

            response = requests.post(
                url=endpoint,
                json=payload,
                headers={
                    'Content-type': JSON_CONTENT_TYPE
                }
            )

        except Exception as e:
            logger.printError(f"Request to client could not be completed: {str(e)}")
            raise error.RpcBadRequestError(
                id=id,
                message=f"Request to client could not be completed: {str(e)}"
            )

        try:
            response = response.json()
        except Exception as e:
            logger.printError(f"Json in client response is not supported: {str(e)}")
            raise error.RpcInternalServerError(
                id=id,
                message=f"Json in client response is not supported: {str(e)}"
            )

        logger.printInfo(f"Response received from {endpoint}: {response}")

        if ERROR in response and response[ERROR] is not None:
            logger.printError(f"Exception occured in server: {response[ERROR]}")
            raise error.RpcBadRequestError(
                id=id,
                message=f"Exception occured in server: {response[ERROR]}"
            )

        return response[RESULT]
