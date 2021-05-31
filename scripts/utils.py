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
        path = input("Please choose the directory to save blockchain data " +
                     f"(/srv/swapper-node/{coin}_{stage}): ")
    except SyntaxError:
        path = f"/srv/swapper-node/{coin}_{stage}"
    if not path:
        path = f"/srv/swapper-node/{coin}_{stage}"
    return path


def queryCerts():
    try:
        sys.stdout.write("WARN: Please note that you need to have the files swapper_cert.key and swapper_cert.crt in "
                         "the certificates directory.\n")
        path = input("Please choose the path of the certs " +
                     f'{"(/etc/ssl/certs): "}')
    except SyntaxError:
        path = f'{"/etc/ssl/certs"}'
    if not path:
        path = f'{"/etc/ssl/certs"}'
    return path


def askSSL():
    while True:
        if queryYesNo("Do you want to activate SSL? ", "no"):
            try:
                sys.stdout.write(
                    "WARN: Please note that you need to have the files swapper_cert.key and swapper_cert.crt in "
                    "the certificates directory.\n")
                path = input(
                    "Please choose the path of the certs " + f'{"(/etc/ssl/certs): "}')
            except SyntaxError:
                path = f'{"/etc/ssl/certs"}'
            if not path:
                path = f'{"/etc/ssl/certs"}'

            if os.path.isdir(path) and "swapper_cert.key" in os.listdir(path) and "swapper_cert.crt" in os.listdir(path):
                os.environ["CERT_PATH"] = path
                os.environ["NGINX_CONFIG_PATH"] = "../../nginx/ssl.conf"
                return
            else:
                sys.stdout.write("You need to have the files swapper_cert.key and swapper_cert.crt in the "
                                 "certificates directory. \n")
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
