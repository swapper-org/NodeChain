#!/usr/bin/python3
from lib2to3.pgen2 import driver
import os
import subprocess
import docker
import utils
import signal
import sys
import argparse
import json
from pathlib import Path
import logger


# "coin" argument is never used. Is declared to prevent errors
def exitSignal(coin=None):
    print("Exiting gracefully, goodbye!")
    raise SystemExit


def checkApiRunning(coin, network):
    for container in client.containers.list():
        if "com.docker.compose.project" in client.containers.get(container.name).attrs["Config"]["Labels"] and client.containers.get(container.name).attrs["Config"]["Labels"]["com.docker.compose.project"] == f"{coin}_{network}_api":
            return True


def checkConnectorRunning():
    for container in client.containers.list():
        if "com.docker.compose.project" in client.containers.get(container.name).attrs["Config"]["Labels"] and client.containers.get(container.name).attrs["Config"]["Labels"]["com.docker.compose.project"] == "connector":
            return True


def createConnectorNetwork(args):
    logger.printInfo("Starting network nodechain-network.", verbosity=args.verbose)
    for network in client.networks.list():
        if network.name == "nodechain-network":
            if args.verbose:
                logger.printInfo("nodechain-network is already started", verbosity=args.verbose)
            return

    client.networks.create("nodechain-network", driver="bridge")


def listRunningApis():
    running = []
    for container in client.containers.list():
        if "com.docker.compose.project" in client.containers.get(container.name).attrs["Config"]["Labels"] and not client.containers.get(container.name).attrs["Config"]["Labels"]["com.docker.compose.project"][:-4] in running:
            running.append(
                client.containers.get(container.name).attrs["Config"]["Labels"]["com.docker.compose.project"][:-4])
    return running


# This method binds the used ports to the ENV variables to stop Connector and Nginx. TODO: this might use only to container and nginx containers in the future
def bindUsedPort(coin, network):
    for container in client.containers.list():
        if "com.docker.compose.project" in client.containers.get(container.name).attrs["Config"]["Labels"] and client.containers.get(container.name).attrs["Config"]["Labels"]["com.docker.compose.project"] == f"{coin}_{network}_api":
            bindings = client.containers.get(
                container.name).attrs["HostConfig"]["PortBindings"]
            if "80/tcp" in bindings:
                os.environ["PORT"] = bindings["80/tcp"][0]["HostPort"]
            if "443/tcp" in bindings:
                os.environ["SSL_PORT"] = bindings["443/tcp"][0]["HostPort"]
    return


def argumentHandler():
    version = utils.getVersion()

    parser = argparse.ArgumentParser(
        description='Nodechain allows the user to build and manage their own nodes natively without having to rely on external services.',
        prog="Nodechain")
    parser.add_argument('-t', '--token', action="store",
                        dest='token', help="symbol of the token", default=None)
    parser.add_argument('-n', '--network', action="store", dest='network',
                        help="network where to set up the blockchain", choices=['mainnet', 'testnet', 'regtest'], default=None)
    parser.add_argument('-p', '--port', action="store", dest='port',
                        help="port to start the node", default=None)
    parser.add_argument('-sp', '--sslport', action="store",
                        dest='ssl_port', help="ssl port", default=None)
    parser.add_argument('-b', '--blockchain', action="store", dest='blockchain_path',
                        help="path to store blockchain files", default=None)
    parser.add_argument('--ssl', action="store_true",
                        dest='config', help="ssl config", default=False)
    parser.add_argument('-c', '--cert', action="store",
                        dest='certs', help="path to certs", default=None)
    parser.add_argument('-V', '--version', action="version",
                        version=f"NodeChain version {version}", help="software version", default=None)
    parser.add_argument("-v", "--verbose", help="Increase output verbosity", action="store_true")

    # Create group to start and stop all apis at the same time
    all = argparse.ArgumentParser(add_help=False)
    all.add_argument('-a', '--all', action='store', dest="all", choices=['mainnet', 'testnet', 'regtest'], help='Network where to set up the blockchain', default=None)

    # Add subparsers to handle verbs
    sp = parser.add_subparsers()
    spStart = sp.add_parser('start', parents=[all], description='Starts the daemon if it is not currently running.', help='Starts %(prog)s daemon')
    spStop = sp.add_parser('stop', parents=[all], description='Stops the daemon if it is currently running.', help='Stops %(prog)s daemon')
    spStatus = sp.add_parser('status', description='Displays information about the nodes', help='Status of %(prog)s daemon')

    # Hook subparsers up to handle start, stop and status
    spStart.set_defaults(func=start)
    spStop.set_defaults(func=stop)
    spStatus.set_defaults(func=status)  # TODO: Change to GUI

    args = parser.parse_args()

    # Print help when no args
    if len(sys.argv) == 1:
        parser.print_help()
        parser.exit()
    else:
        args.func(args)

    return args


def start(args):
    os.chdir(ROOT_DIR)
    if args.verbose:
        logger.printInfo(f"Working directory: {ROOT_DIR}", verbosity=args.verbose)

    utils.showMainTitle()
    utils.showSubtitle("CONNECTOR CONFIG")

    if checkConnectorRunning():
        logger.printInfo("Connector is already started.", verbosity=args.verbose)
    else:
        utils.connectorQueries(args)
        createConnectorNetwork(args)
        startConnector(args)

    # TODO: This method might contain errors. This will be used once we have only one Connector container for all apis
    # if args.all:
    #     for token in listAvailableTokens():
    #         if args.all in listAvailableNetworksByToken(token):
    #             os.environ["COIN"] = token
    #             os.environ["NETWORK"] = args.all
    #             utils.queryPath(token, args.all)
    #             if checkApiRunning(token, args.all):
    #                 logger.printError(f"The API {token} in {args.all} network is already started.", verbosity=args.verbose)
    #             # startApi(token, args.all)
    # else:
    #     token = coinMenu(args)
    #     if args.verbose:
    #         logger.printInfo(f"Token selected: {token}", verbosity=args.verbose)
    #     network = networkMenu(args, token)
    #     if args.verbose:
    #         logger.printInfo(f"Network selected: {network}", verbosity=args.verbose)
    #     utils.queryPath(args, token, network)
    #     if checkApiRunning(token, network):
    #         logger.printError(f"The API {token} in {network} network is already started.", verbosity=args.verbose)
    #         return
    #     startApi(args, token, network)


def stop(args):
    os.chdir(ROOT_DIR)
    if args.verbose:
        logger.printInfo(f"Working directory: {ROOT_DIR}", verbosity=args.verbose)

    utils.showMainTitle()
    # TODO: This method might contain errors. This will be used once we have only one Connector container for all apis
    if args.all:
        for token in listAvailableTokens():
            if args.all in listAvailableNetworksByToken(token):
                os.environ["COIN"] = token
                os.environ["NETWORK"] = args.all
                if not checkApiRunning(token, args.all):
                    logger.printError(f"Can't stop {token} in {args.all}. Containers are not running", verbosity=args.verbose)
                    continue
                bindUsedPort(token, args.all)
                # stopApi(token, args.all)
    else:
        token = coinMenu(args)
        if args.verbose:
            logger.printInfo(f"Token selected: {token}")
        network = networkMenu(args, token)
        if args.verbose:
            logger.printInfo(f"Network selected: {network}")
        if not checkApiRunning(token, network):
            logger.printError(f"Can't stop the API {token} in {network}. Containers are not running.", verbosity=args.verbose)
            return
        bindUsedPort(token, network)
        stopApi(args, token, network)


def status(args):
    os.chdir(ROOT_DIR)
    if args.verbose:
        logger.printInfo(f"Working directory: {ROOT_DIR}", verbosity=args.verbose)
    utils.showMainTitle()
    token = coinMenu(args)
    if args.verbose:
        logger.printInfo(f"Token selected: {token}")
    network = networkMenu(args, token)
    if args.verbose:
        logger.printInfo(f"Network selected: {network}")
    statusApi(args, token, network)


def listAvailableCoins():
    coins = []
    with open('.availableCurrencies.json') as f:
        data = json.load(f)
        for api in data:
            coins.append(api["name"])
    return coins


def listAvailableTokens():
    tokens = []
    with open('.availableCurrencies.json') as f:
        data = json.load(f)
        for api in data:
            tokens.append(api["token"])
    return tokens


def listAvailableNetworksByToken(token):
    with open('.availableCurrencies.json') as f:
        data = json.load(f)
        for api in data:
            if api["token"] == token:
                return dict.keys(api["networks"])


def coinMenu(args):
    tokens = utils.listTokens()
    if args.token and args.token in tokens:
        os.environ["COIN"] = args.token
        return args.token
    else:
        menu = utils.fillMenu(listAvailableCoins, blockchainChoice, exitSignal)
        utils.showSubtitle("BLOCKCHAIN SELECTION")
        runningApis = listRunningApis()
        for key in sorted(menu.keys())[:-1]:
            if any(utils.getTokenFromCoin(menu[key][0]) in substring for substring in runningApis):
                print("{}{}.{}".format("[RUNNING]", str(key).rjust(7), menu[key][0].capitalize()))
            else:
                print("{}{}.{}".format("[OFF]", str(key).rjust(11), menu[key][0].capitalize()))

        print("{}.{}".format(str(len(sorted(menu.keys()))).rjust(16), menu[sorted(menu.keys())[-1]][0].capitalize()))

        coin = input("Please choose the blockchain that you want to use to build up/stop the node(1-{options}): ".format(
            options=(len(listAvailableCoins()) + 1)))
        menu.get(coin, [None, utils.invalid])[1](menu[coin][0])

        return utils.getTokenFromCoin(menu[coin][0])  # TODO: CHECK


def networkMenu(args, token):
    if args.network:
        os.environ["NETWORK"] = args.network
        return args.network
    else:
        menu = utils.fillMenu(lambda: listAvailableNetworksByToken(token), networkChoice, exitSignal)
        utils.showSubtitle("NETWORK SELECTION")
        runningApis = listRunningApis()
        for key in sorted(menu.keys())[:-1]:
            if f"{token}_{menu[key][0]}" in runningApis:
                print("{}{}.{}".format("[RUNNING]", str(key).rjust(7), menu[key][0].capitalize()))
            else:
                print("{}{}.{}".format("[OFF]", str(key).rjust(11), menu[key][0].capitalize()))

        print("{}.{}".format(str(len(sorted(menu.keys()))).rjust(16), menu[sorted(menu.keys())[-1]][0].capitalize()))

        network = input("Please choose the network that you want to use (1-{options}): ".format(
            options=(len(listAvailableNetworksByToken(token)) + 1)))
        menu.get(network, [None, utils.invalid])[1](menu[network][0])

        return menu[network][0]


def blockchainChoice(coin):
    os.environ["COIN"] = utils.getTokenFromCoin(coin.lower())


def networkChoice(network):
    os.environ["NETWORK"] = network.lower()


def getDockerComposePath(token, network):
    path = ""

    if network not in listAvailableNetworksByToken(token):
        print(f"Can't find {token} in {network}")
        return

    with open('.availableCurrencies.json') as f:
        data = json.load(f)
        for api in data:
            if api["token"] == token:
                path = Path(api["networks"][network]["dockerComposePath"])

    return path.parent.absolute()


def startApi(args, token, network):
    path = getDockerComposePath(token, network)
    logger.printInfo(f"Starting {token}_{network}_api node... This might take a while.")
    if args.verbose:
        logger.printEnvs()
        logger.printInfo(f"Path to docker file: {path}", verbosity=args.verbose)

    sp = subprocess.Popen(["docker-compose", "-f", f"{token}.yml", "-p", f"{token}_{network}_api", "up", "--build", "-d"],
                          stdin=FNULL, stdout=FNULL, stderr=subprocess.PIPE, cwd=str(path))
    err = sp.communicate()
    if sp.returncode == 0:
        logger.printInfo(f"{token}_{network}_api node started", verbosity=args.verbose)
    else:
        logger.printError(f"An error occurred while trying to start {token}_{network}_api: \n", verbosity=args.verbose)
        logger.printError(err[1].decode("ascii"), verbosity=args.verbose)
        raise SystemExit


def stopApi(args, token, network):
    path = getDockerComposePath(token, network)
    logger.printInfo(f"Stopping {token}_{network}_api node... This might take a while.", verbosity=args.verbose)
    if args.verbose:
        logger.printEnvs()
        logger.printInfo(f"Path to docker file: {path}", verbosity=args.verbose)

    sp = subprocess.Popen(["docker-compose", "-f", f"{token}.yml", "-p", f"{token}_{network}_api", "down"],
                          stdin=FNULL, stdout=FNULL, stderr=subprocess.PIPE, cwd=str(path))
    err = sp.communicate()
    if sp.returncode == 0:
        logger.printInfo(f"{token}_{network}_api node stopped", verbosity=args.verbose)
    else:
        logger.printError(f"An error occurred while trying to stop {token}_{network}_api: \n", verbosity=args.verbose)
        logger.printError(err[1].decode("ascii"), verbosity=args.verbose)
        raise SystemExit


def statusApi(args, token, network):
    logger.printInfo(f"Getting information of {token}_{network}_api containers...", verbosity=args.verbose)
    if args.verbose:
        logger.printEnvs()

    utils.showSubtitle(f"{token.upper()} {network.upper()} INFORMATION")
    services = utils.listServices(token, network)
    for container in client.containers.list():
        dockerContainer = client.containers.get(container.name)
        if "com.docker.compose.project" in dockerContainer.attrs["Config"]["Labels"] and dockerContainer.attrs["Config"]["Labels"]["com.docker.compose.project"] == f"{token}_{network}_api" and dockerContainer.attrs["Config"]["Labels"]["com.docker.compose.service"] in services:
            if dockerContainer.attrs["State"]["Status"] == 'running':
                print("{}{}".format("[RUNNING]".ljust(15), str(dockerContainer.attrs["Config"]["Labels"]["com.docker.compose.service"]).capitalize()))
            else:
                print("{}{}".format("[OFF]".ljust(15), str(dockerContainer.attrs["Config"]["Labels"]["com.docker.compose.service"]).capitalize()))


def startConnector(args):
    path = Path("./docker-compose/connector.yml")
    path = path.parent.absolute()
    logger.printInfo("Starting connector and reverse proxy... This might take a while.")
    if args.verbose:
        logger.printEnvs()
        logger.printInfo(f"Path to docker file: {path}", verbosity=args.verbose)

    sp = subprocess.Popen(["docker-compose", "-f", "connector.yml", "-p", "connector", "up", "--build", "-d"],
                          stdin=FNULL, stdout=FNULL, stderr=subprocess.PIPE, cwd=str(path))
    err = sp.communicate()
    if sp.returncode == 0:
        logger.printInfo("Connector has been started", verbosity=args.verbose)
    else:
        logger.printError("An error occurred while trying to start connector container or nginx container: \n", verbosity=args.verbose)
        logger.printError(err[1].decode("ascii"), verbosity=args.verbose)
        raise SystemExit


if __name__ == "__main__":

    FNULL = open(os.devnull, 'w')
    ROOT_DIR = os.path.dirname(os.path.abspath(os.path.join(__file__, os.pardir)))

    signal.signal(signal.SIGINT, utils.signalHandler)
    client = docker.from_env()

    args = argumentHandler()
