#!/usr/bin/python3
import os
import subprocess
import docker
import utils
import signal

FNULL = open(os.devnull, 'w')


def setup(coin, stage):
    os.chdir(f"../docker-compose/{stage}")
    print("Starting " + f"{coin}_{stage}_api node...")
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
    print("Stopping " + f"{coin}_{stage}_api node...")
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


def invalid():
    print("INVALID CHOICE!")


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
        os.environ["PORT"] = utils.queryPort("Port to start: ")
        os.environ["BLOCKCHAIN_PATH"] = utils.queryPath(
            os.environ["COIN"].lower(), os.environ["STAGE"].lower())
        os.environ["SSL_PORT"] = utils.queryPort("Port to start (SSL): ")
        utils.askSSL()
        setup(os.environ["COIN"].lower(), os.environ["STAGE"].lower())


def apiChoice(coin):
    os.environ["COIN"] = coin.upper()
    checkStatus()


def stageChoice(stage):
    os.environ["STAGE"] = stage.upper()
    apiMenu()


def apiMenu():
    menu = utils.fillMenu(listApis, apiChoice, exitSetup)
    utils.showSubtitle("BLOCKCHAIN SELECTION")
    for key in sorted(menu.keys()):
        if (menu[key][0]+"_{stage}".format(stage=os.environ["STAGE"].lower())) in listRunningApis():
            print("[RUNNING]" + "\t" + key + "." + menu[key][0])
        else:
            print("[OFF]" + "\t" + key + "." + menu[key][0])

    ans = input(
        "Please pick a node to start/stop (1-{options}): ".format(options=(len(listApis()) + 1)))
    menu.get(ans, [None, invalid])[1](menu[ans][0].upper())


def stageMenu():
    menu = utils.fillMenu(listStages, stageChoice, exitSetup)
    utils.showSubtitle("ENVIRONMENT SELECTION")
    for key in sorted(menu.keys()):
        print(key + "." + menu[key][0])

    stage = input("Please choose the environment that you want to use to build up/stop the node(1-{options}): ".format(
        options=(len(listStages()) + 1)))
    menu.get(stage, [None, invalid])[1](menu[stage][0].upper())


signal.signal(signal.SIGINT, utils.signalHandler)
client = docker.from_env()
utils.showMainTitle()

stageMenu()
