import sys
import os
from datetime import datetime
from tabnanny import verbose


def printInfo(*argv, sep='', end='\n', file=sys.stdout, flush=True, verbosity=False):
    if verbosity:
        print(f"[INFO][{datetime.now()}] ", *argv, sep=sep, end=end, file=file, flush=flush)
    else:
        print(f"", *argv, sep=sep, end=end, file=file, flush=flush)


def printWarning(*argv, sep='', end='\n', file=sys.stdout, flush=True):
    print(f"[WARNING][{datetime.now()}] ", *argv, sep=sep, end=end, file=file, flush=flush)


def printError(*argv, sep='', end='\n', file=sys.stdout, flush=True):
    print(f"[ERROR][{datetime.now()}] ", *argv, sep=sep, end=end, file=file, flush=flush)


def printEnvs():
    port = os.getenv("PORT")
    blockchainPath = os.getenv("BLOCKCHAIN_PATH")
    sslPort = os.getenv("SSL_PORT")  # TODO: We might remove this in the future
    token = os.getenv("COIN")
    network = os.getenv("NETWORK")
    configFile = os.getenv("NGINX_CONFIG_PATH")
    certsPath = os.getenv("CERT_PATH")

    printInfo(f"[ENVIRONMENTAL INFO] Token: {token} | Network: {network} | Port: {port} | Blockchain Path: {blockchainPath} | SSL Port: {sslPort} | Config File: {configFile} | Path to ssl certs: {certsPath}")
