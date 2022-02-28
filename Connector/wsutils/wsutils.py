#!/usr/bin/python3
from .constants import WS_METHOD


def isWsEnpointPath(method):
    return method == WS_METHOD
