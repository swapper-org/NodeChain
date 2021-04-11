#!/usr/bin/python3
import sys
import os


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
            sys.stdout.write("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")


def queryPort(question):
    while True:
        sys.stdout.write(question)
        port = input().lower()
        if not port.isnumeric():
            sys.stdout.write("Port must be a number, please respond with a valid port. \n")
        else:
            return port


def queryPath(coin):
    try:
        path = input("Please choose the directory to save blockchain data " + f"(/srv/swapper-node/{coin}): ")
    except SyntaxError:
        path = f"/srv/swapper-node/{coin}"
    if not path:
        path = f"/srv/swapper-node/{coin}"
    return path


def queryCerts():
    try:
        sys.stdout.write("WARN: Please note that you need to have the files swapper_cert.key and swapper_cert.crt in "
                         "the certificates directory.\n")
        path = input("Please choose the path of the certs " + f"(/etc/ssl/certs): ")
    except SyntaxError:
        path = f"/etc/ssl/certs"
    if not path:
        path = f"/etc/ssl/certs"
    return path


def askSSL():
    while True:
        if queryYesNo("Do you want to activate SSL? ", "no"):
            try:
                sys.stdout.write(
                    "WARN: Please note that you need to have the files swapper_cert.key and swapper_cert.crt in "
                    "the certificates directory.\n")
                path = input("Please choose the path of the certs " + f"(/etc/ssl/certs): ")
            except SyntaxError:
                path = f"/etc/ssl/certs"
            if not path:
                path = f"/etc/ssl/certs"

            if os.path.isdir(path) and "swapper_cert.key" in os.listdir(path) and "swapper_cert.crt" in os.listdir(path):
                os.environ["CERT_PATH"] = path
                os.environ["NGINX_CONFIG_PATH"] = "../nginx/ssl.conf"
                return
            else:
                sys.stdout.write("You need to have the files swapper_cert.key and swapper_cert.crt in the "
                                 "certificates directory. \n")
        else:
            os.environ["NGINX_CONFIG_PATH"] = "../nginx/nginx.conf"
            os.environ["CERT_PATH"] = "/etc/ssl/certs"
            return
