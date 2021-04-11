webSockets = []
webSocketMethods = {}

def webSocket (f):
    webSockets.append(f)
    return f


def webSocketMethod (f):
    webSocketMethods[f.__name__] = f
    return f