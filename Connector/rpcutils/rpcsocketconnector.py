#!/usr/bin/python
import json
import socket
from logger import logger
from . import error
from .constants import *


class RPCSocketConnector():

    @staticmethod
    def request(hostname, port, id, method, params):

        try:

            payload = {
                ID: id,
                METHOD: method,
                PARAMS: params,
                JSON_RPC: JSON_RPC_VERSION
            }

            logger.printInfo(f"Making RPC socket request to {hostname}:{port}. Payload: {payload}")

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((hostname, port))

            jsonText = {"jsonrpc": JSON_RPC_VERSION, "method": method, "params": params, "id": id}

            s.send(json.dumps(jsonText).encode())
            s.send('\n'.encode())

            chunks = []
            while True:
                chunk = s.recv(2048)
                chunks.append(chunk)
                if chunk[-1:] == b'\n':
                    break

            s.close()

            responseStr = b''.join(chunks).decode('ascii')

        except Exception as e:
            logger.printError(f"Request to client could not be completed: {str(e)}")
            raise error.RpcBadRequestError(
                id=id,
                message=f"Request to client could not be completed: {str(e)}"
            )

        try:
            response = json.loads(responseStr)
        except Exception as e:
            logger.printError(f"Json in client response is not supported: {str(e)}")
            raise error.RpcInternalServerError(
                id=id,
                message=f"Json in client response is not supported: {str(e)}"
            )

        logger.printInfo(f"Response received from {hostname}:{port}: {response}")

        if ERROR in response and response[ERROR] is not None:
            logger.printError(f"Exception occured in server: {response[ERROR]}")
            raise error.RpcBadRequestError(
                id=id,
                message=f"Exception occured in server: {response[ERROR]}"
            )

        return response[RESULT]
