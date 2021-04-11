#!/usr/bin/python3
import os
import subprocess
import docker
import utils

FNULL = open(os.devnull, 'w')


def setup(coin):
    os.chdir("../docker-compose")
    print("Starting " + f"{coin}_api node...")
    sp = subprocess.Popen(["docker-compose", "-f", f"{coin}.yml", "-p", f"{coin}_api", "up", "--build", "-d"],
                     stdin=FNULL, stdout=FNULL, stderr=subprocess.PIPE)
    err = sp.communicate()
    if sp.returncode == 0:
        print(f"{coin}_api node started")
    else:
        print(f"An error occurred while trying to start {coin}_api:")
        print("\n")
        print(err[1].decode("ascii"))


def stop(coin):
    os.chdir("../docker-compose")
    print("Stopping " + f"{coin}_api node...")
    sp = subprocess.Popen(["docker-compose", "-f", f"{coin}.yml", "-p", f"{coin}_api", "down"],
                     stdin=FNULL, stdout=FNULL, stderr=subprocess.PIPE)
    err = sp.communicate()
    if sp.returncode == 0:
        print(f"{coin}_api node stopped")
    else:
        print(f"An error occurred while trying to start {coin}_api:")
        print("\n")
        print(err[1].decode("ascii"))


def exitSetup():
    print("Exiting...")
    raise SystemExit


def invalid():
    print("INVALID CHOICE!")


def checkIfRunning(coin):
    for container in client.containers.list():
        if "com.docker.compose.project" in client.containers.get(container.name).attrs["Config"]["Labels"] and client.containers.get(container.name).attrs["Config"]["Labels"]["com.docker.compose.project"] == f"{coin}_api":
            return True


def listRunningContainers():
    running = []
    for container in client.containers.list():
        if "com.docker.compose.project" in client.containers.get(container.name).attrs["Config"]["Labels"] and not client.containers.get(container.name).attrs["Config"]["Labels"]["com.docker.compose.project"] in running:
            running.append(
                client.containers.get(container.name).attrs["Config"]["Labels"]["com.docker.compose.project"][:-4])
    return running


def listApis():
    composes = os.listdir("../docker-compose")
    return [f[:-4] for f in composes]


def getUsedPort(coin):
    for container in client.containers.list():
        if "com.docker.compose.project" in client.containers.get(container.name).attrs["Config"]["Labels"] and client.containers.get(container.name).attrs["Config"]["Labels"]["com.docker.compose.project"] == f"{coin}_api":
            bindings = client.containers.get(container.name).attrs["HostConfig"]["PortBindings"]
            if "80/tcp" in bindings:
                os.environ["PORT"] = bindings["80/tcp"][0]["HostPort"]
            if "443/tcp" in bindings:
                os.environ["SSL_PORT"] = bindings["443/tcp"][0]["HostPort"]
    return


def checkStatus():
    if checkIfRunning(os.environ["COIN"].lower()):
        getUsedPort(os.environ["COIN"].lower())
        stop(os.environ["COIN"].lower())
    else:
        os.environ["PORT"] = utils.queryPort("Port to start: ")
        os.environ["BLOCKCHAIN_PATH"] = utils.queryPath(os.environ["COIN"].lower())
        os.environ["SSL_PORT"] = utils.queryPort("Port to start (SSL): ")
        utils.askSSL()
        os.environ["STAGE"] = "PRO"
        setup(os.environ["COIN"].lower())


def apiChoice(coin):
    os.environ["COIN"] = coin.upper()
    checkStatus()



client = docker.from_env()
menu = {}
counter = 1

for coinContainer in listApis():
    menu[str(counter)] = (coinContainer, apiChoice)
    counter += 1

menu[str(len(listApis()) + 1)] = ("Exit", exitSetup)

for key in sorted(menu.keys()):
    if menu[key][0] in listRunningContainers():
        print("[RUNNING]"+"\t" + key + "." + menu[key][0])
    else:
        print("[OFF]"+"\t" + key + "." + menu[key][0])

ans = input("Please pick a server to start/stop (1-{options}): ".format(options=(len(listApis()) + 1)))
menu.get(ans, [None, invalid])[1](menu[ans][0].upper())
