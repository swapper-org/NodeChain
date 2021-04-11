#!/usr/bin/python3
import json
import os
from webapp import WebApp
from aiohttp import web
import aiohttp
from wsutils.serverwebsocket import ServerWebSocket
from rpcutils import rpcutils, errorhandler as rpcErrorHandler
from wsutils import wsutils
from wsutils.subscriptionshandler import SubcriptionsHandler
import importlib


importlib.__import__(os.environ['COIN'].lower())


async def rpcServerHandler(request):

    reqParsed = None

    try:

        reqParsed = rpcutils.parseRpcRequest(await request.read())

        if reqParsed[rpcutils.METHOD] in rpcutils.RPCMethods:
            payload = rpcutils.RPCMethods[reqParsed[rpcutils.METHOD]](reqParsed[rpcutils.ID], reqParsed[rpcutils.PARAMS])
        else:
            raise rpcErrorHandler.MethodNotAllowedError("RPC Method not supported for " + os.environ['COIN'])

        return web.Response(
            text=json.dumps(
                rpcutils.generateRPCResultResponse(
                    reqParsed[rpcutils.ID],
                    payload
                )
            ),
            content_type=rpcutils.JSON_CONTENT_TYPE
        )

    except rpcErrorHandler.Error as e:

        return web.Response(
            text=json.dumps(
                rpcutils.generateRPCErrorResponse(
                    reqParsed[rpcutils.ID] if reqParsed is not None else rpcutils.UNKNOWN_RPC_REQUEST_ID,
                    e.jsonEncode()
                )
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

                if reqParsed[rpcutils.METHOD] == "close":
                    await ws.websocket.close()

                elif reqParsed[rpcutils.METHOD] not in wsutils.webSocketMethods:
                    raise rpcErrorHandler.BadRequestError("WS Method not supported for " + os.environ['COIN'])
                    
                else:
                    payload = wsutils.webSocketMethods[reqParsed[rpcutils.METHOD]](ws, reqParsed[rpcutils.ID], reqParsed[rpcutils.PARAMS])
                    await ws.websocket.send_str(
                        json.dumps(
                            rpcutils.generateRPCResultResponse(
                                reqParsed[rpcutils.ID],
                                payload
                            )
                        )
                    )

            elif msg.type == aiohttp.WSMsgType.ERROR:
                raise rpcErrorHandler.InternalServerError('ws connection closed with exception %s' % ws.websocket.exception())

    except rpcErrorHandler.Error as e:
        await ws.websocket.send_str(
            json.dumps(
                rpcutils.generateRPCResultResponse(
                    reqParsed[rpcutils.ID] if reqParsed is not None else rpcutils.UNKNOWN_RPC_REQUEST_ID,
                    e.jsonEncode()
                )
            )
        )
        
    SubcriptionsHandler.removeClient(ws)
    return ws


if __name__ == '__main__':
    print("Server started")
    app = WebApp()
    app.add_routes([web.post('/rpc', rpcServerHandler)])
    app.add_routes([web.get('/ws', websocketServerHandler)])

    for webSocket in wsutils.webSockets:
        webSocket()

    web.run_app(app, port=80)
