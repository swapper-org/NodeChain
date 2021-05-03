import sys
from datetime import datetime


def printInfo(*argv, sep='', end='\n', file=sys.stdout, flush=True):
    print(f"[INFO][{datetime.now()}] ", *argv, sep=sep, end=end, file=file, flush=flush)


def printWarning():
    print(f"[WARNING][{datetime.now()}] ", *argv, sep=sep, end=end, file=file, flush=flush)


def printError():
    print(f"[ERROR][{datetime.now()}] ", *argv, sep=sep, end=end, file=file, flush=flush)
