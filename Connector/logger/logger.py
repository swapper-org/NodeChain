import sys
from datetime import datetime


def printInfo(*argv, sep='', end='\n', file=sys.stdout, flush=True):
    # TODO: Uncomment this line when a verbose mode is implemented
    # print(f"[INFO][{datetime.now()}] ", *argv, sep=sep, end=end, file=file, flush=flush)
    return


def printWarning(*argv, sep='', end='\n', file=sys.stdout, flush=True):
    print(f"[WARNING][{datetime.now()}] ", *argv, sep=sep, end=end, file=file, flush=flush)


def printError(*argv, sep='', end='\n', file=sys.stdout, flush=True):
    print(f"[ERROR][{datetime.now()}] ", *argv, sep=sep, end=end, file=file, flush=flush)
