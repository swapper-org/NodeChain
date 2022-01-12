#!/usr/bin/python3
import sys
import os
import argparse
import json


def queryYesNo(question, default="yes"):
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n]: "
    elif default == "yes":
        prompt = " [Y/n]: "
    elif default == "no":
        prompt = " [y/N]: "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write(
                "Please respond with 'yes' or 'no' (or 'y' or 'n').\n")


def queryPort(question):
    while True:
        sys.stdout.write(question)
        port = input().lower()
        if not port.isnumeric():
            sys.stdout.write(
                "Port must be a number, please respond with a valid port. \n")
        else:
            return port


def queryPath(coin, stage):
    try:
        path = input(f"Please choose the directory to save blockchain data (/srv/nodechain-node/{coin}_{stage}): ")
    except SyntaxError:
        path = f"/srv/nodechain-node/{coin}_{stage}"
    if not path:
        path = f"/srv/nodechain-node/{coin}_{stage}"
    return path


def queryCerts(certs):
    if not certs:
        try:
            sys.stdout.write("WARN: Please note that you need to have the files nodechain_cert.key and nodechain_cert.crt in "
                             "the certificates directory.\n")
            path = input("Please choose the path of the certs (/etc/ssl/certs): ")
        except SyntaxError:
            path = "/etc/ssl/certs"
        if not path:
            path = "/etc/ssl/certs"
    else:
        path = certs
    return path


def askSSL(config, certs):
    if config is None:
        while True:
            if queryYesNo("Do you want to activate SSL? ", "no"):
                path = queryCerts(certs)

                if os.path.isdir(path) and "nodechain_cert.key" in os.listdir(path) and "nodechain_cert.crt" in os.listdir(path):
                    os.environ["CERT_PATH"] = path
                    os.environ["NGINX_CONFIG_PATH"] = "../../nginx/ssl.conf"
                    return
                else:
                    sys.stdout.write("You need to have the files nodechain_cert.key and nodechain_cert.crt in the "
                                     "certificates directory. \n")
            else:
                os.environ["NGINX_CONFIG_PATH"] = "../../nginx/nginx.conf"
                os.environ["CERT_PATH"] = "/etc/ssl/certs"
                return
    elif config:
        while True:
            path = queryCerts(certs)
            if os.path.isdir(path) and "nodechain_cert.key" in os.listdir(path) and "nodechain_cert.crt" in os.listdir(path):
                os.environ["CERT_PATH"] = path
                os.environ["NGINX_CONFIG_PATH"] = "../../nginx/ssl.conf"
                return
    else:
        os.environ["NGINX_CONFIG_PATH"] = "../../nginx/nginx.conf"
        os.environ["CERT_PATH"] = "/etc/ssl/certs"
        return


def fillMenu(listFnc, choiceFnc, exitFnc):
    menu = {}
    counter = 1
    for item in listFnc():
        menu[str(counter)] = (item, choiceFnc)
        counter += 1

    menu[str(len(listFnc()) + 1)] = ("Exit", exitFnc)

    return menu


def showMainTitle():
    print(r"---------------------------------------------------")
    print(r"  _  _          _        ___  _                   ")
    print(r" | \| | ___  __| | ___  / __|| |_   __ _ (_) _ _  ")
    print(r" | .` |/ _ \/ _` |/ -_)| (__ | ' \ / _` || || ' \ ")
    print(r" |_|\_|\___/\__,_|\___| \___||_||_|\__,_||_||_||_|")
    print(r"---------------------------------------------------")


def showSubtitle(subtitle):
    print("===================================================")
    print(f"\t\t{subtitle}")
    print("===================================================")


def signalHandler(sig, frame):
    print('Exiting gracefully, goodbye!')
    sys.exit(0)


def getVersion():
    os.chdir("../Connector/")
    f = open('config.json')
    data = json.load(f)
    return data['version']


def argumentHandler():
    version = getVersion()

    parser = argparse.ArgumentParser(
        description='Nodechain allows the user to build and manage their own nodes natively without having to rely on external services.', prog="python3 nodechain.py")
    parser.add_argument('-t', '--token', action="store",
                        dest='token', help="symbol of the token", default=None)
    parser.add_argument('-n', '--network', action="store", dest='network',
                        help="network where to set up the blockchain", choices=['mainnet', 'testnet', 'development'], default=None)
    parser.add_argument('-p', '--port', action="store", dest='port',
                        help="port to start the node", default=None)
    parser.add_argument('-sp', '--sslport', action="store",
                        dest='ssl_port', help="ssl port", default=None)
    parser.add_argument('-b', '--blockchain', action="store", dest='blockchain_path',
                        help="path to store blockchain files", default=None)
    parser.add_argument('--ssl', action="store_true",
                        dest='config', help="ssl config", default=None)
    parser.add_argument('--no-ssl', action="store_false",
                        dest='config', help="no ssl config", default=None)
    parser.add_argument('-c', '--cert', action="store",
                        dest='certs', help="path to certs", default=None)
    parser.add_argument('-v', '--version', action="version",
                        version=f"NodeChain version {version}", help="software version", default=None)

    subparsers = parser.add_subparsers(help="Script handling")

    subparsers.add_parser('start', help="Start any NodeChain API")

    subparsers.add_parser('stop', help="Stop any NodeChain API")

    if len(sys.argv) == 1:
        parser.print_help()
        parser.exit()

    args = parser.parse_args()

    return args
