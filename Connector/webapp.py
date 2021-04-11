from aiohttp import web


class WebApp(web.Application):

    instance = None

    def __new__(cls):

        if not WebApp.instance:
            WebApp.instance = web.Application()
        
        return WebApp.instance
    

