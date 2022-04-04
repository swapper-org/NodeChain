#!/usr/bin/python
import requests
from logger import logger
from . import error
from .constants import INTERNAL_SERVER_ERROR_CODE


class HTTPConnector:

    @staticmethod
    def get(endpoint, path="", params=None, headers=None):

        response = None
        try:

            logger.printInfo(f"Making HTTP Get request to {endpoint}. Params: {params}")

            response = requests.get(
                url=f"{endpoint}{path}",
                params=params,
                headers=headers
            )
            response.raise_for_status()

        except requests.exceptions.HTTPError as err:
            logger.printError(f"HTTP Error making request to {endpoint}: {err}")
            raise error.Error(
                message=f"HTTP Error making request to {endpoint}",
                code=response.status_code if response is not None else INTERNAL_SERVER_ERROR_CODE
            )

        except requests.exceptions.ConnectionError as err:
            logger.printError(f"Connection Error making request to {endpoint}: {err}")
            raise error.NotFoundError(message=f"{endpoint} not found")

        except requests.exceptions.Timeout as err:
            logger.printError(f"Timeout Error making request to {endpoint}: {err}")
            raise error.TimeoutError(message=f"Timeout error making request to {endpoint}")

        except requests.exceptions.RequestException as err:
            logger.printError(f"Request Error making request to {endpoint}: {err}")
            raise error.InternalServerError(message=f"Request Error making request to {endpoint}")

        try:
            response = response.json()
        except Exception as err:
            logger.printError(f"Json in client response is not supported: {str(err)}")
            raise error.InternalServerError(
                message=f"Json in client response is not supported: {str(err)}"
            )

        logger.printInfo(f"Response received from {endpoint}: {response}")

        return response

    @staticmethod
    def post(endpoint, path="", data=None, json=None):

        response = None
        try:

            logger.printInfo(f"Making HTTP Post request to {endpoint}.")

            response = requests.post(
                url=f"{endpoint}{path}",
                data=data,
                json=json
            )
            response.raise_for_status()

        except requests.exceptions.HTTPError as err:
            logger.printError(f"HTTP Error making request to {endpoint}: {err}")
            raise error.Error(
                message=f"HTTP Error making request to {endpoint}",
                code=response.status_code if response is not None else INTERNAL_SERVER_ERROR_CODE
            )

        except requests.exceptions.ConnectionError as err:
            logger.printError(f"Connection Error making request to {endpoint}: {err}")
            raise error.NotFoundError(message=f"{endpoint} not found")

        except requests.exceptions.Timeout as err:
            logger.printError(f"Timeout Error making request to {endpoint}: {err}")
            raise error.TimeoutError(message=f"Timeout error making request to {endpoint}")

        except requests.exceptions.RequestException as err:
            logger.printError(f"Request Error making request to {endpoint}: {err}")
            raise error.InternalServerError(message=f"Request Error making request to {endpoint}")

        try:
            response = response.json()
        except Exception as err:
            logger.printError(f"Json in client response is not supported: {str(err)}")
            raise error.InternalServerError(
                message=f"Json in client response is not supported: {str(err)}"
            )

        logger.printInfo(f"Response received from {endpoint}: {response}")

        return response
