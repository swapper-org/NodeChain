#!/usr/bin/python
import json
import asyncio
from asyncio import streams
from logger import logger
from . import error
from .constants import *


class RPCSocketConnector:

    @staticmethod
    async def request(endpoint, id, method, params):

        try:

            payload = {
                "id": id,
                "method": method,
                "params": params,
                "jsonrpc": JSON_RPC_VERSION
            }

            try:
                hostname, port = endpoint.split(":")[:2]
                port = int(port)
            except ValueError as e:
                logger.printError(f"Node endpoint bad format: {e}")
                raise error.RpcBadRequestError(
                    id=id,
                    message="Bad request"
                )

            logger.printInfo(f"Making RPC socket request to {hostname}:{port}. Payload: {payload}")

            reader, writer = await asyncio.open_connection(hostname, port)
            writer.write((json.dumps(payload) + "\n").encode())
            await writer.drain()

            data = await reader.readuntil(separator=b'\n')

            responseStr = data.decode()

            writer.close()
            await writer.wait_closed()

        except streams.IncompleteReadError or streams.LimitOverrunError as e:
            logger.printError(f"Response could not be retrieve from node: {str(e)}")
            raise error.RpcBadGatewayError(
                id=id,
                message="Bad gateway"
            )
        except OSError as e:
            logger.printError(f"Can not connect to node: {str(e)}")
            raise error.RpcNotFoundError(
                id=id,
                message="Node not found"
            )

        try:
            response = json.loads(responseStr)
        except TypeError as e:
            logger.printError(f"Response from node is not JSON format: {str(e)}")
            raise error.RpcBadGatewayError(
                id=id,
                message="Bad gateway"
            )

        logger.printInfo(f"Response received from {hostname}:{port}: {response}")

        if "error" in response and response["error"] is not None:
            logger.printError(f"Exception occurred in server: {response['error']}")
            raise error.RpcBadRequestError(
                id=id,
                message="Bad request"
            )

        return response["result"]
