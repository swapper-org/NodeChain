#!/usr/bin/python3
import aiohttp
from aiohttp import web
import importlib
import json
import os
from logger import logger
from rpcutils import rpcutils, errorhandler as rpcErrorHandler
from wsutils.serverwebsocket import ServerWebSocket
from wsutils import wsutils
from wsutils.subscriptionshandler import SubcriptionsHandler
from webapp import WebApp

logger.printInfo(f"Loading connector for {os.environ['COIN']}")
importlib.__import__(os.environ['COIN'].lower())


async def rpcServerHandler(request):

    reqParsed = None

    try:

        reqParsed = rpcutils.parseRpcRequest(await request.read())
        logger.printInfo(f"New RPC request received: {reqParsed}")

        if reqParsed[rpcutils.METHOD] in rpcutils.RPCMethods:
            payload = rpcutils.RPCMethods[reqParsed[rpcutils.METHOD]](reqParsed[rpcutils.ID], reqParsed[rpcutils.PARAMS])
        else:
            logger.printError(f"RPC Method not supported for {os.environ['COIN']}")
            raise rpcErrorHandler.MethodNotAllowedError(f"RPC Method not supported for {os.environ['COIN']}")

        response = rpcutils.generateRPCResultResponse(
            reqParsed[rpcutils.ID],
            payload
        )

        logger.printInfo(f"Sending response to requestor: {response}")

        return web.Response(
            text=json.dumps(
                response
            ),
            content_type=rpcutils.JSON_CONTENT_TYPE
        )

    except rpcErrorHandler.Error as e:

        response = rpcutils.generateRPCErrorResponse(
            reqParsed[rpcutils.ID] if reqParsed is not None else rpcutils.UNKNOWN_RPC_REQUEST_ID,
            e.jsonEncode()
        )

        logger.printError(f"Sending RPC response to requestor: {response}")

        return web.Response(
            text=json.dumps(
                response
            ),
            content_type=rpcutils.JSON_CONTENT_TYPE,
            status=e.code
        )


async def websocketServerHandler(request):
    
    ws = ServerWebSocket()
    await ws.websocket.prepare(request)

    reqParsed = None

    try:

        async for msg in ws.websocket:

            if msg.type == aiohttp.WSMsgType.TEXT:

                reqParsed = rpcutils.parseRpcRequest(msg.data)
                logger.printInfo(f"New WS request received: {reqParsed}")

                if reqParsed[rpcutils.METHOD] == "close":
                    logger.printInfo(f"Closing WS connection with client")
                    await ws.websocket.close()

                elif reqParsed[rpcutils.METHOD] not in wsutils.webSocketMethods:
                    logger.printError(f"WS Method not supported for {os.environ['COIN']}")
                    raise rpcErrorHandler.BadRequestError(f"WS Method not supported for {os.environ['COIN']}")
                    
                else:

                    payload = wsutils.webSocketMethods[reqParsed[rpcutils.METHOD]](ws, reqParsed[rpcutils.ID], reqParsed[rpcutils.PARAMS])
                    
                    response = rpcutils.generateRPCResultResponse(
                        reqParsed[rpcutils.ID],
                        payload
                    )
                    logger.printInfo(f"Sending WS response to requestor: {response}")

                    await ws.websocket.send_str(
                        json.dumps(
                            response
                        )
                    )

            elif msg.type == aiohttp.WSMsgType.ERROR:
                logger.printError('WS connection closed with exception %s' % ws.websocket.exception())
                raise rpcErrorHandler.InternalServerError('WS connection closed with exception %s' % ws.websocket.exception())

    except rpcErrorHandler.Error as e:

        response = rpcutils.generateRPCResultResponse(
            reqParsed[rpcutils.ID] if reqParsed is not None else rpcutils.UNKNOWN_RPC_REQUEST_ID,
            e.jsonEncode()
        )
        logger.printError(f"Sending RPC response to requestor: {response}")

        await ws.websocket.send_str(
            json.dumps(
                response
            )
        )
        
    SubcriptionsHandler.removeClient(ws)
    return ws


def runServer():
    app = WebApp()
    app.add_routes([web.post('/rpc', rpcServerHandler)])
    app.add_routes([web.get('/ws', websocketServerHandler)])

    for webSocket in wsutils.webSockets:
        webSocket()

    logger.printInfo("Starting connector")
    web.run_app(app, port=80)


if __name__ == '__main__':
    runServer()
