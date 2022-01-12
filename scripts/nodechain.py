#!/usr/bin/python3
import os
import subprocess
import docker
import utils
import signal
import sys
import argparse


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


def apiChoice(coin):
    os.environ["COIN"] = coin.lower()
    checkStatus()


def stageChoice(stage):
    os.environ["STAGE"] = stage.lower()
    apiMenu()


def apiMenu():
    apis = listApis()
    if args.token and args.token in apis:
        os.environ["COIN"] = args.token
        checkStatus()
    else:
        menu = utils.fillMenu(listApis, apiChoice, exitSetup)
        utils.showSubtitle("BLOCKCHAIN SELECTION")
        for key in sorted(menu.keys()):
            if (menu[key][0] + "_{stage}".format(stage=os.environ["STAGE"].lower())) in listRunningApis():
                print("[RUNNING]" + "\t" + key + "." + menu[key][0])
            else:
                print("[OFF]" + "\t" + key + "." + menu[key][0])

        ans = input(
            "Please pick a node to start/stop (1-{options}): ".format(options=(len(listApis()) + 1)))
        menu.get(ans, [None, utils.invalid])[1](menu[ans][0].upper())


def stageMenu():
    if args.network:
        os.environ["STAGE"] = args.network.lower()
        apiMenu()
    else:
        menu = utils.fillMenu(listStages, stageChoice, exitSetup)
        utils.showSubtitle("ENVIRONMENT SELECTION")
        for key in sorted(menu.keys()):
            print(key + "." + menu[key][0])

        stage = input("Please choose the environment that you want to use to build up/stop the node(1-{options}): ".format(
            options=(len(listStages()) + 1)))
        menu.get(stage, [None, utils.invalid])[1](menu[stage][0].upper())


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
    all.add_argument('-a', '--all', action='store', dest="network", choices=['mainnet', 'testnet', 'development'], help='Network where to set up the blockchain', default=None)

    # Add subparsers to handle verbs
    sp = parser.add_subparsers()
    spStart = sp.add_parser('start', parents=[all], description='Starts the daemon if it is not currently running.', help='Starts %(prog)s daemon')
    spStop = sp.add_parser('stop', parents=[all], description='Stops the daemon if it is currently running.', help='Stops %(prog)s daemon')
    spStatus = sp.add_parser('status', description='Displays information about the nodes', help='Status of %(prog)s daemon')

    # Hook subparsers up to handle start, stop and status
    spStart.set_defaults(func=startTest)
    spStop.set_defaults(func=stopTest)
    spStatus.set_defaults(func=status)  # TODO: Change to GUI

    args = parser.parse_args()
    args.func(args)

    return args


def startTest(args):
    if args.all:
        print("start all apis")
    else:
        print("starting")


def stopTest(args):
    if args.all:
        print("stop all apis")
    else:
        print("stoping")


def status(args):
    print("status")


if __name__ == "__main__":
    args = argumentHandler()
    print(args)
    FNULL = open(os.devnull, 'w')

    signal.signal(signal.SIGINT, utils.signalHandler)
    client = docker.from_env()

    # utils.showMainTitle()

    # stageMenu()
