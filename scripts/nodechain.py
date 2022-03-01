#!/usr/bin/python3
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
import endpoints


# "token" argument is never used. Is declared to prevent errors
def exitSignal(token=None):
    print("Exiting gracefully, goodbye!")
    raise SystemExit


def checkApiRunning(token, network):
    for container in client.containers.list():
        if "com.docker.compose.project" in client.containers.get(container.name).attrs["Config"]["Labels"] and client.containers.get(container.name).attrs["Config"]["Labels"]["com.docker.compose.project"] == f"{token}{network}api":
            return True


def checkConnectorRunning():
    for container in client.containers.list():
        if "com.docker.compose.project" in client.containers.get(container.name).attrs["Config"]["Labels"] and client.containers.get(container.name).attrs["Config"]["Labels"]["com.docker.compose.project"] == "connector":
            return True


def createConnectorNetwork(args):
    logger.printInfo("Starting network nodechain-network.", verbosity=args.verbose)
    for network in client.networks.list():
        if network.name == "nodechain-network":
            logger.printInfo("nodechain-network is already started", verbosity=args.verbose)
            return

    client.networks.create("nodechain-network", driver="bridge")


def listRunningApis():
    running = []
    for container in client.containers.list():
        if "com.docker.compose.project" in client.containers.get(container.name).attrs["Config"]["Labels"] and not client.containers.get(container.name).attrs["Config"]["Labels"]["com.docker.compose.project"][:-4] in running:
            running.append(
                client.containers.get(container.name).attrs["Config"]["Labels"]["com.docker.compose.project"][:-3])
    return running


# This method binds the used ports to the ENV variables to stop Connector and Nginx.
def bindUsedPort():
    for container in client.containers.list():
        if "com.docker.compose.project" in client.containers.get(container.name).attrs["Config"]["Labels"] and client.containers.get(container.name).attrs["Config"]["Labels"]["com.docker.compose.project"] == "connector":
            bindings = client.containers.get(
                container.name).attrs["HostConfig"]["PortBindings"]
            if "80/tcp" in bindings:
                os.environ["PORT"] = bindings["80/tcp"][0]["HostPort"]
            if "443/tcp" in bindings:
                os.environ["SSL_PORT"] = bindings["443/tcp"][0]["HostPort"]
    return


# Start/Stop all apis by network
# PARAMS:
# args.all -> contains the information of the chosen network
# mode -> ['start', 'stop']
def handleAllApisByNetwork(args, mode):
    for token in listAvailableTokens():
        if args.all in listAvailableNetworksByToken(token):
            os.environ["COIN"] = token
            os.environ["NETWORK"] = args.all
            if mode == 'start':
                utils.queryPath(args, token, args.all)
                if checkApiRunning(token, args.all):
                    logger.printError(f"The API {token} in {args.all} network is already started.", verbosity=args.verbose)
                startApi(args, token, args.all)
            else:
                if not checkApiRunning(token, args.all):
                    logger.printError(f"Can't stop {token} in {args.all}. Containers are not running", verbosity=args.verbose)
                    continue
                stopApi(args, token, args.all)


# Stop all APIs
def stopAllApis(args):
    for token in listAvailableTokens():
        os.environ["COIN"] = token
        for network in listAvailableNetworksByToken(token):
            os.environ["NETWORK"] = network
            if not checkApiRunning(token, network):
                logger.printError(f"Can't stop {token} in {network}. Containers are not running", verbosity=args.verbose)
                continue
            stopApi(args, token, network)


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

    if args.all:
        handleAllApisByNetwork(args, 'start')
    else:
        token = coinMenu(args)
        if args.verbose:
            logger.printInfo(f"Token selected: {token}", verbosity=args.verbose)
        network = networkMenu(args, token)
        if args.verbose:
            logger.printInfo(f"Network selected: {network}", verbosity=args.verbose)
        utils.queryPath(args, token, network)
        if checkApiRunning(token, network):
            logger.printError(f"The API {token} in {network} network is already started.", verbosity=args.verbose)
            return
        startApi(args, token, network)


def stop(args):
    os.chdir(ROOT_DIR)
    if args.verbose:
        logger.printInfo(f"Working directory: {ROOT_DIR}", verbosity=args.verbose)

    utils.showMainTitle()
    utils.showSubtitle("CONNECTOR CONFIG")

    logger.connectorNotRunning(checkConnectorRunning(), args)

    if args.verbose:
        logger.printWarning("Stopping the connector will stop all running APIs", verbosity=args.verbose)
    if utils.queryYesNo("Do you want to stop the connector?", default="no"):
        logger.printInfo("Stopping all APIs...", verbosity=args.verbose)
        stopAllApis(args)
        bindUsedPort()
        stopConnector(args)
    else:
        if args.verbose:
            logger.printInfo("Connector won't shut down.", verbosity=args.verbose)

        if args.all:
            handleAllApisByNetwork(args, 'stop')
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
            stopApi(args, token, network)


def status(args):
    os.chdir(ROOT_DIR)
    if args.verbose:
        logger.printInfo(f"Working directory: {ROOT_DIR}", verbosity=args.verbose)
    utils.showMainTitle()
    choice = configMenu()
    if choice == 'connector':
        logger.connectorNotRunning(checkConnectorRunning(), args)
        if args.verbose:
            logger.printInfo("Showing connector status information.", verbosity=args.verbose)
        statusConnector(args)
    elif choice == 'apis':
        logger.connectorNotRunning(checkConnectorRunning(), args)
        if args.verbose:
            logger.printInfo("Showing connector status information.", verbosity=args.verbose)
        token = coinMenu(args)
        if args.verbose:
            logger.printInfo(f"Token selected: {token}")
        network = networkMenu(args, token)
        if args.verbose:
            logger.printInfo(f"Network selected: {network}")
        statusApi(args, token, network)
    else:
        logger.printError("Error trying to get the status of NodeChain", verbosity=args.verbose)
        raise SystemExit


def listAvailableCoins():
    coins = []
    with open(utils.AVAILABLE_CURRENCIES) as f:
        data = json.load(f)
        for api in data:
            coins.append(api["name"])
    return coins


def listAvailableTokens():
    tokens = []
    with open(utils.AVAILABLE_CURRENCIES) as f:
        data = json.load(f)
        for api in data:
            tokens.append(api["token"])
    return tokens


def listAvailableNetworksByToken(token):
    with open(utils.AVAILABLE_CURRENCIES) as f:
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
            if f"{token}{menu[key][0]}" in runningApis:
                print("{}{}.{}".format("[RUNNING]", str(key).rjust(7), menu[key][0].capitalize()))
            else:
                print("{}{}.{}".format("[OFF]", str(key).rjust(11), menu[key][0].capitalize()))

        print("{}.{}".format(str(len(sorted(menu.keys()))).rjust(16), menu[sorted(menu.keys())[-1]][0].capitalize()))

        network = input("Please choose the network that you want to use (1-{options}): ".format(
            options=(len(listAvailableNetworksByToken(token)) + 1)))
        menu.get(network, [None, utils.invalid])[1](menu[network][0])

        return menu[network][0]


def configMenu():
    menu = utils.fillMenu(lambda: ["Connector", "APIs"], configChoice, exitSignal)
    utils.showSubtitle("STATUS SELECTION")
    for key in sorted(menu.keys())[:-1]:
        # TODO: Add some way to find out if connector or any api is running
        if checkConnectorRunning():
            print("{}{}.{}".format("[RUNNING]", str(key).rjust(7), menu[key][0].capitalize()))
        else:
            print("{}{}.{}".format("[OFF]", str(key).rjust(11), menu[key][0].capitalize()))

    print("{}.{}".format(str(len(sorted(menu.keys()))).rjust(16), menu[sorted(menu.keys())[-1]][0].capitalize()))

    choice = input("Please choose any option to show its status (1-{options}): ".format(
        options=(len(["Connector", "APIs"]) + 1)))
    menu.get(choice, [None, utils.invalid])[1](menu[choice][0])

    return (menu[choice][0]).lower()


def blockchainChoice(coin):
    os.environ["COIN"] = utils.getTokenFromCoin(coin.lower())


def networkChoice(network):
    os.environ["NETWORK"] = network.lower()


def configChoice(choice):
    return


def getDockerComposePath(token, network):
    path = ""

    if network not in listAvailableNetworksByToken(token):
        print(f"Can't find {token} in {network}")
        return

    with open(utils.AVAILABLE_CURRENCIES) as f:
        data = json.load(f)
        for api in data:
            if api["token"] == token:
                path = Path(api["networks"][network]["dockerComposePath"])

    return path.parent.absolute()


def startApi(args, token, network):
    path = getDockerComposePath(token, network)
    logger.printInfo(f"Starting {token}{network}api node... This might take a while.")
    if args.verbose:
        logger.printEnvs()
        logger.printInfo(f"Path to docker file: {path}", verbosity=args.verbose)

    sp = subprocess.Popen(["docker-compose", "-f", f"{token}.yml", "-p", f"{token}{network}api", "up", "--build", "-d"],
                          stdin=FNULL, stdout=FNULL, stderr=subprocess.PIPE, cwd=str(path))
    err = sp.communicate()
    if sp.returncode == 0:
        logger.printInfo(f"{token}{network}api node started", verbosity=args.verbose)
    else:
        logger.printError(f"An error occurred while trying to start {token}{network}api: \n", verbosity=args.verbose)
        logger.printError(err[1].decode("ascii"), verbosity=args.verbose)
        raise SystemExit

    # Get port to make requests
    bindUsedPort()

    # Add currency to the connector
    if utils.queryYesNo("Do you want to configure your API ", default="no"):
        response = endpoints.addApi(args, token, network, os.environ["PORT"], defaultConfig=False)
    else:
        response = endpoints.addApi(args, token, network, os.environ["PORT"])
    # Already registered
    if not response:
        return
    # If response is an error we need to shut down the API
    if response.status_code != 200:
        stopApi(args, token, network)
    else:
        response = response.json()
        # If response["success"] is an internal connector error so we also need to shut down the API
        if response["success"] is False:
            stopApi(args, token, network)


def stopApi(args, token, network):
    path = getDockerComposePath(token, network)
    logger.printInfo(f"Stopping {token}{network}api node... This might take a while.", verbosity=args.verbose)
    if args.verbose:
        logger.printEnvs()
        logger.printInfo(f"Path to docker file: {path}", verbosity=args.verbose)

    sp = subprocess.Popen(["docker-compose", "-f", f"{token}.yml", "-p", f"{token}{network}api", "down"],
                          stdin=FNULL, stdout=FNULL, stderr=subprocess.PIPE, cwd=str(path))
    err = sp.communicate()
    if sp.returncode == 0:
        logger.printInfo(f"{token}{network}api node stopped", verbosity=args.verbose)
    else:
        logger.printError(f"An error occurred while trying to stop {token}{network}api: \n", verbosity=args.verbose)
        logger.printError(err[1].decode("ascii"), verbosity=args.verbose)
        raise SystemExit


def statusApi(args, token, network):
    logger.printInfo(f"Getting information of {token}{network}api containers...", verbosity=args.verbose)
    if args.verbose:
        logger.printEnvs()

    utils.showSubtitle(f"{token.upper()} {network.upper()} INFORMATION")
    services = utils.listServices(token, network)
    for container in client.containers.list():
        dockerContainer = client.containers.get(container.name)
        if "com.docker.compose.project" in dockerContainer.attrs["Config"]["Labels"] and dockerContainer.attrs["Config"]["Labels"]["com.docker.compose.project"] == f"{token}{network}api" and dockerContainer.attrs["Config"]["Labels"]["com.docker.compose.service"] in services:
            if str(dockerContainer.attrs["State"]["Status"]) == 'running':
                print("{}{}".format("[RUNNING]".ljust(15), str(dockerContainer.attrs["Config"]["Labels"]["com.docker.compose.service"]).capitalize()))
            else:
                print("{}{}".format("[OFF]".ljust(15), str(dockerContainer.attrs["Config"]["Labels"]["com.docker.compose.service"]).capitalize()))


def startConnector(args):
    path = Path("./docker-compose/connector.yml")
    path = path.parent.absolute()
    logger.printInfo("Starting connector and reverse proxy... This might take a while.", verbosity=args.verbose)
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


def stopConnector(args):
    path = Path("./docker-compose/connector.yml")
    path = path.parent.absolute()

    logger.printInfo("Stopping connector and reverse proxy... This might take a while.", verbosity=args.verbose)
    if args.verbose:
        logger.printEnvs()
        logger.printInfo(f"Path to docker file: {path}", verbosity=args.verbose)

    sp = subprocess.Popen(["docker-compose", "-f", "connector.yml", "-p", "connector", "down"],
                          stdin=FNULL, stdout=FNULL, stderr=subprocess.PIPE, cwd=str(path))
    err = sp.communicate()
    if sp.returncode == 0:
        logger.printInfo("Connector has been stopped", verbosity=args.verbose)
    else:
        logger.printError("An error occurred while trying to stop connector container or nginx container: \n", verbosity=args.verbose)
        logger.printError(err[1].decode("ascii"), verbosity=args.verbose)
        raise SystemExit


def statusConnector(args):
    logger.printInfo("Getting information of connector containers...", verbosity=args.verbose)
    if args.verbose:
        logger.printEnvs()

    utils.showSubtitle("CONNECTOR INFORMATION")
    for container in client.containers.list():
        dockerContainer = client.containers.get(container.name)
        if "com.docker.compose.project" in dockerContainer.attrs["Config"]["Labels"] and dockerContainer.attrs["Config"]["Labels"]["com.docker.compose.project"] == "connector" and dockerContainer.attrs["Config"]["Labels"]["com.docker.compose.service"] in ["connector", "nginx"]:
            if dockerContainer.attrs["State"]["Status"] == 'running':
                print("{}{}".format("[RUNNING]".ljust(15), str(dockerContainer.attrs["Config"]["Labels"]["com.docker.compose.service"]).capitalize()))
            else:
                print("{}{}".format("[OFF]".ljust(15), str(dockerContainer.attrs["Config"]["Labels"]["com.docker.compose.service"]).capitalize()))


if __name__ == "__main__":

    FNULL = open(os.devnull, 'w')
    ROOT_DIR = os.path.dirname(os.path.abspath(os.path.join(__file__, os.pardir)))

    signal.signal(signal.SIGINT, utils.signalHandler)
    client = docker.from_env()

    args = argumentHandler()
