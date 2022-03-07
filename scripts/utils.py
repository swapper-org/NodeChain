import sys
import os
import json
import logger

AVAILABLE_CURRENCIES = "./Connector/.availableCurrencies.json"


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


def connectorQueries(args):
    os.environ["PORT"] = args.port if args.port else queryPort(args, "Port to start: ")

    if args.ssl_port:
        os.environ["SSL_PORT"] = args.ssl_port
    else:
        os.environ["SSL_PORT"] = queryPort(args, "Port to start (SSL): ")

    querySSL(args.config, args.certs)


def queryConfigurable(args, question, configurable):
    while True:
        response = input(question).lower()
        if not response:
            logger.printError("Can't configure with empty answers.", verbosity=args.verbose)
            sys.stdout.write(f"Please respond with with a valid text for {configurable}")
        else:
            return response


def queryPort(args, question):
    while True:
        sys.stdout.write(question)
        port = input().lower()
        if not port.isnumeric():
            logger.printError("Can't configure with empty answers.", verbosity=args.verbose)
            sys.stdout.write(
                "Port must be a number, please respond with a valid port. \n")
        else:
            return port


def queryPath(args, coin, network):
    if args.blockchain_path:
        os.environ["BLOCKCHAIN_PATH"] = args.blockchain_path
    else:
        try:
            path = input(f"Please choose the directory to save blockchain data (/srv/nodechain-node/{coin}_{network}): ")
        except SyntaxError:
            path = f"/srv/nodechain-node/{coin}_{network}"
        if not path:
            path = f"/srv/nodechain-node/{coin}_{network}"

        os.environ["BLOCKCHAIN_PATH"] = path
        if args.verbose:
            logger.printInfo(f"Blockchain path selected: {path}", verbosity=args.verbose)


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


# This method will be expecting your nodechain_cert.key and nodechain_cert.crt
def querySSL(config, certs):
    if config:
        while True:
            path = queryCerts(certs)
            if os.path.isdir(path) and "nodechain_cert.key" in os.listdir(path) and "nodechain_cert.crt" in os.listdir(path):
                os.environ["CERT_PATH"] = path
                os.environ["NGINX_CONFIG_PATH"] = "../nginx/ssl.conf"
                return
    else:
        os.environ["NGINX_CONFIG_PATH"] = "../nginx/nginx.conf"
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
    f = open('../Connector/config.json')
    data = json.load(f)
    return data['version']


def invalid():
    print("INVALID CHOICE!")


def listTokens():
    tokens = []
    with open(AVAILABLE_CURRENCIES) as f:
        data = json.load(f)
        for api in data:
            tokens.append(api["token"])
    return tokens


def listNetworksByToken(token):
    with open(AVAILABLE_CURRENCIES) as f:
        data = json.load(f)
        for api in data:
            if api["token"] == token:
                return dict.keys(api["networks"])


def listNameTokens():
    coins = []
    with open(AVAILABLE_CURRENCIES) as f:
        data = json.load(f)
        for api in data:
            coins.append(api["name"])
    return coins


def listServices(token, network):
    with open(AVAILABLE_CURRENCIES) as f:
        data = json.load(f)
        for api in data:
            if api["token"] == token:
                return api["networks"][network]["services"]


def getTokenFromCoin(token):
    with open(AVAILABLE_CURRENCIES) as f:
        data = json.load(f)
        for api in data:
            if api["name"] == token:
                return api["token"]


def getTokenConfiguration(token, network):
    with open(AVAILABLE_CURRENCIES) as f:
        data = json.load(f)
        for api in data:
            if api["token"] == token:
                return api["networks"][network]["configurable"]


def formatApiData(args, data):
    logger.printInfo(json.dumps(data, sort_keys=True, indent=4), verbosity=args.verbose)
