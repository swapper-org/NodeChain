from . import errorhandler
from .constants import *
import requests
from logger import logger


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
                endpoint,
                json=payload,
                headers={
                    'Content-type': JSON_CONTENT_TYPE
                }
            )

        except Exception as e:
            logger.printError(f"Request to client could not be completed: {str(e)}")
            raise errorhandler.BadRequestError(f"Request to client could not be completed: {str(e)}")

        try:
            response = response.json()
        except Exception as e:
            logger.printError(f"Json in client response is not supported: {str(e)}")
            raise errorhandler.InternalServerError(f"Json in client response is not supported: {str(e)}")

        logger.printInfo(f"Response received from {endpoint}: {response}")

        if ERROR in response and response[ERROR] is not None:
            logger.printError(f"Exception occured in server: {response[ERROR]}")
            raise errorhandler.BadRequestError(f"Exception occured in server: {response[ERROR]}")

        return response[RESULT]
