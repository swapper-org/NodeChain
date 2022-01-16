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


# "coin" argument is never used. Is declared to prevent errors
def exitSignal(coin=None):
    print("Exiting gracefully, goodbye!")
    raise SystemExit


def checkIfRunning(coin, network):
    for container in client.containers.list():
        if "com.docker.compose.project" in client.containers.get(container.name).attrs["Config"]["Labels"] and client.containers.get(container.name).attrs["Config"]["Labels"]["com.docker.compose.project"] == f"{coin}_{network}_api":
            return True


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
    parser.add_argument('-v', '--version', action="version",
                        version=f"NodeChain version {version}", help="software version", default=None)

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
    if args.all:
        print("start all apis")
    else:
        utils.showMainTitle()
        token = coinMenu(args)
        network = networkMenu(args, token)
        utils.configQueries(args, token, network)
        if checkIfRunning(token, network):
            print(f"The API {token} in {network} network is already started.")
            return
        startApi(token, network)


def stop(args):
    os.chdir(ROOT_DIR)
    if args.all:
        print("stop all apis")
    else:
        utils.showMainTitle()
        token = coinMenu(args)
        network = networkMenu(args, token)
        if not checkIfRunning(token, network):
            print("Can't stop the api. Containers are not running")
            return
        bindUsedPort(token, network)
        stopApi(token, network)


def status(args):
    os.chdir(ROOT_DIR)
    utils.showMainTitle()
    token = coinMenu(args)
    network = networkMenu(args, token)
    statusApi(token, network)


def listAvailableCoins():
    coins = []
    with open('.availableCurrencies.json') as f:
        data = json.load(f)
        for api in data:
            coins.append(api["name"])
    return coins


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

        # Return the coin if needed
        return menu[network][0]  # TODO: CHECK


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


def startApi(token, network):
    path = getDockerComposePath(token, network)
    sp = subprocess.Popen(["docker-compose", "-f", f"{token}.yml", "-p", f"{token}_{network}_api", "up", "--build", "-d"],
                          stdin=FNULL, stdout=FNULL, stderr=subprocess.PIPE, cwd=str(path))
    err = sp.communicate()
    if sp.returncode == 0:
        print(f"{token}_{network}_api node started")
    else:
        print(f"An error occurred while trying to start {token}_{network}_api:")
        print("\n")
        print(err[1].decode("ascii"))
        raise SystemExit


def stopApi(token, network):
    path = getDockerComposePath(token, network)
    print(f"Stopping {token}_{network}_api node...")
    sp = subprocess.Popen(["docker-compose", "-f", f"{token}.yml", "-p", f"{token}_{network}_api", "down"],
                          stdin=FNULL, stdout=FNULL, stderr=subprocess.PIPE, cwd=str(path))
    err = sp.communicate()
    if sp.returncode == 0:
        print(f"{token}_{network}_api node stopped")
    else:
        print(f"An error occurred while trying to start {token}_{network}_api:")
        print("\n")
        print(err[1].decode("ascii"))


def statusApi(token, network):
    print(f"Getting information of {token}_{network}_api containers...")
    utils.showSubtitle(f"{token.upper()} {network.upper()} INFORMATION")
    services = utils.listServices(token, network)
    for container in client.containers.list():
        dockerContainer = client.containers.get(container.name)
        if "com.docker.compose.project" in dockerContainer.attrs["Config"]["Labels"] and dockerContainer.attrs["Config"]["Labels"]["com.docker.compose.project"] == f"{token}_{network}_api" and dockerContainer.attrs["Config"]["Labels"]["com.docker.compose.service"] in services:
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
