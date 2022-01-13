#!/usr/bin/python3
import os
import subprocess
import docker
import utils
import signal
import sys
import argparse
import json


def setup(coin, stage):
    os.chdir(f"../docker-compose/{stage}")
    print(f"Starting {coin}_{stage}_api node...")
    sp = subprocess.Popen(["docker-compose", "-f", f"{coin}.yml", "-p", f"{coin}_{stage}_api", "up", "--build", "-d"],
                          stdin=FNULL, stdout=FNULL, stderr=subprocess.PIPE)
    err = sp.communicate()
    if sp.returncode == 0:
        print(f"{coin}_{stage}_api node started")
    else:
        print(f"An error occurred while trying to start {coin}_{stage}_api:")
        print("\n")
        print(err[1].decode("ascii"))


def stop(coin, stage):
    os.chdir(f"../docker-compose/{stage}")
    print(f"Stopping {coin}_{stage}_api node...")
    sp = subprocess.Popen(["docker-compose", "-f", f"{coin}.yml", "-p", f"{coin}_{stage}_api", "down"],
                          stdin=FNULL, stdout=FNULL, stderr=subprocess.PIPE)
    err = sp.communicate()
    if sp.returncode == 0:
        print(f"{coin}_{stage}_api node stopped")
    else:
        print(f"An error occurred while trying to start {coin}_{stage}_api:")
        print("\n")
        print(err[1].decode("ascii"))


# "coin" argument is never used. Is declared to prevent errors
def exitSetup(coin=None):
    print("Exiting gracefully, goodbye!")
    raise SystemExit


def checkIfRunning(coin, stage):
    for container in client.containers.list():
        if "com.docker.compose.project" in client.containers.get(container.name).attrs["Config"]["Labels"] and client.containers.get(container.name).attrs["Config"]["Labels"]["com.docker.compose.project"] == f"{coin}_{stage}_api":
            return True


def listRunningApis():
    running = []
    for container in client.containers.list():
        if "com.docker.compose.project" in client.containers.get(container.name).attrs["Config"]["Labels"] and not client.containers.get(container.name).attrs["Config"]["Labels"]["com.docker.compose.project"][:-4] in running:
            running.append(
                client.containers.get(container.name).attrs["Config"]["Labels"]["com.docker.compose.project"][:-4])
    return running


def listApis():
    composes = os.listdir(
        "../docker-compose/{stage}".format(stage=os.environ["STAGE"].lower()))

    # Trim last 4 characters for every "coin.yml" to remove the ".yml" part
    return [f[:-4] for f in composes]


def listStages():
    return os.listdir("../docker-compose")


def getUsedPort(coin, stage):
    for container in client.containers.list():
        if "com.docker.compose.project" in client.containers.get(container.name).attrs["Config"]["Labels"] and client.containers.get(container.name).attrs["Config"]["Labels"]["com.docker.compose.project"] == f"{coin}_{stage}_api":
            bindings = client.containers.get(
                container.name).attrs["HostConfig"]["PortBindings"]
            if "80/tcp" in bindings:
                os.environ["PORT"] = bindings["80/tcp"][0]["HostPort"]
            if "443/tcp" in bindings:
                os.environ["SSL_PORT"] = bindings["443/tcp"][0]["HostPort"]
    return


def checkStatus():
    if checkIfRunning(os.environ["COIN"].lower(), os.environ["STAGE"].lower()):
        getUsedPort(os.environ["COIN"].lower(), os.environ["STAGE"].lower())
        stop(os.environ["COIN"].lower(), os.environ["STAGE"].lower())
    else:
        if args.port:
            os.environ["PORT"] = args.port
        else:
            os.environ["PORT"] = utils.queryPort("Port to start: ")

        if args.blockchain_path:
            os.environ["BLOCKCHAIN_PATH"] = args.blockchain_path
        else:
            os.environ["BLOCKCHAIN_PATH"] = utils.queryPath(
                os.environ["COIN"].lower(), os.environ["STAGE"].lower())

        if args.ssl_port:
            os.environ["SSL_PORT"] = args.ssl_port
        else:
            os.environ["SSL_PORT"] = utils.queryPort("Port to start (SSL): ")

        utils.askSSL(args.config, args.certs)
        setup(os.environ["COIN"].lower(), os.environ["STAGE"].lower())


def argumentHandler():
    version = utils.getVersion()

    parser = argparse.ArgumentParser(
        description='Nodechain allows the user to build and manage their own nodes natively without having to rely on external services.',
        prog="Nodechain")
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
                        dest='config', help="ssl config", default=False)
    parser.add_argument('-c', '--cert', action="store",
                        dest='certs', help="path to certs", default=None)
    parser.add_argument('-v', '--version', action="version",
                        version=f"NodeChain version {version}", help="software version", default=None)

    # Create group to start and stop all apis at the same time
    all = argparse.ArgumentParser(add_help=False)
    all.add_argument('-a', '--all', action='store', dest="all", choices=['mainnet', 'testnet', 'development'], help='Network where to set up the blockchain', default=None)

    # Add subparsers to handle verbs
    sp = parser.add_subparsers()
    spStart = sp.add_parser('start', parents=[all], description='Starts the daemon if it is not currently running.', help='Starts %(prog)s daemon')
    spStop = sp.add_parser('stop', parents=[all], description='Stops the daemon if it is currently running.', help='Stops %(prog)s daemon')
    spStatus = sp.add_parser('status', description='Displays information about the nodes', help='Status of %(prog)s daemon')

    # Hook subparsers up to handle start, stop and status
    spStart.set_defaults(func=start)
    spStop.set_defaults(func=stopTest)
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
    if args.all:
        print("start all apis")
    else:
        utils.showMainTitle()
        token = coinMenu(args)
        network = networkMenu(args)
        print(token)
        print(network)


def stopTest(args):
    if args.all:
        print("stop all apis")
    else:
        print("stoping")


def status(args):
    print("status")


def listAvailableCoins():
    coins = []
    with open('../.config.json') as f:
        data = json.load(f)
        for api in data:
            coins.append(api["name"])
    return coins


def listAvailableNetworks(coin):
    with open('../.config.json') as f:
        data = json.load(f)
        for api in data:
            if api["name"] == coin:
                return dict.keys(api["networks"])


def coinMenu(args):
    tokens = utils.listTokens()
    if args.token and args.token in tokens:
        os.environ["COIN"] = args.token
        # checkStatus()
        print(f"Argument -t {args.token}")
    else:
        menu = utils.fillMenu(listAvailableCoins, blockchainChoice, exitSetup)
        utils.showSubtitle("BLOCKCHAIN SELECTION")
        for key in sorted(menu.keys()):
            print(key + "." + menu[key][0].capitalize())

        coin = input("Please choose the blockchain that you want to use to build up/stop the node(1-{options}): ".format(
            options=(len(listAvailableCoins()) + 1)))
        menu.get(coin, [None, utils.invalid])[1](menu[coin][0])

        # Return the coin if needed
        return utils.getTokenFromCoin(menu[coin][0])  # TODO: CHECK


def networkMenu(args):
    if args.network:
        os.environ["COIN"] = args.network
        # checkStatus()
        print(f"Argument -n {args.network}")
    else:
        menu = utils.fillMenu(listAvailableNetworks, networkChoice, exitSetup)
        utils.showSubtitle("NETWORK SELECTION")
        for key in sorted(menu.keys()):
            print(key + "." + menu[key][0].capitalize())

        network = input("Please choose the blockchain that you want to use to build up/stop the node(1-{options}): ".format(
            options=(len(listAvailableNetworks()) + 1)))
        menu.get(network, [None, utils.invalid])[1](menu[network][0])

        # Return the coin if needed
        return menu[network][0]  # TODO: CHECK


def blockchainChoice(coin):
    os.environ["COIN"] = coin.lower()
    print(f"Moneda elegida {coin}")
    # checkStatus()


def networkChoice(network):
    os.environ["STAGE"] = network.lower()
    print(f"Network elegida {network}")


if __name__ == "__main__":

    FNULL = open(os.devnull, 'w')

    signal.signal(signal.SIGINT, utils.signalHandler)
    client = docker.from_env()

    args = argumentHandler()
    print(args)
