import requests
import logger
import utils

ADD_CURRENCY = "addcoin"
GET_CURRENCY = "getcoin"
UPDATE_CURRENCY = "updatecoin"
REMOVE_CURRENCY = "removecoin"


def addApi(args, token, network, port, defaultConfig=True):
    # Getting API information
    status_code, response = getApi(args, token, network, port)

    # Check if API is registered
    if status_code != 200:
        logger.printError(f"Request to client could not be completed: {status_code}", verbosity=args.verbose)

    response = response.json()
    if response["success"] is True:
        logger.printError(f"API {token} {network} is already registered: {response}", verbosity=args.verbose)
        return

    if defaultConfig:
        payload = {
            "coin": token,
            "network": network,
            "config": {}
        }

    else:
        configurable = utils.getTokenConfiguration(token, network)
        userData = []
        for configOption in configurable:
            userData.append(utils.queryConfigurable(args, f"Please, introduce a value for {configOption}: ", configOption))

        config = dict(zip(configurable, userData))
        payload = {
            "coin": token,
            "network": network,
            "config": config
        }

    headers = {
        'Content-Type': 'application/json'
    }
    if args.verbose:
        logger.printInfo(f"Request payload: {payload}", verbosity=args.verbose)
    try:
        req = requests.post(
            url=f"http://localhost:{port}/admin/{ADD_CURRENCY}",
            json=payload,
            headers=headers
        )

        if args.verbose:
            logger.printInfo(f"Request sent to http://localhost:{port}/admin/{ADD_CURRENCY}: {req.json()}", verbosity=args.verbose)
        return req
    except Exception as e:
        logger.printError(f"Request to client could not be completed: {str(e)}", verbosity=args.verbose)
        return e


def getApi(args, token, network, port):
    payload = {
        "coin": token,
        "network": network,
    }
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        req = requests.post(
            url=f"http://localhost:{port}/admin/{GET_CURRENCY}",
            json=payload,
            headers=headers
        )

        if args.verbose:
            logger.printInfo(f"Request sent to http://localhost:{port}/admin/{GET_CURRENCY}: {req.json()}", verbosity=args.verbose)
        return req.status_code, req
    except Exception as e:
        logger.printError(f"Request to client could not be completed: {str(e)}", verbosity=args.verbose)
        return e


def removeApi(args, token, network, port):
    # Getting API information
    try:
        status_code, response = getApi(args, token, network, port)
    except Exception as e:
        logger.printError(f"Request to client could not be completed: {str(e)}", verbosity=args.verbose)

    # Check if API is not registered
    if status_code != 200:
        logger.printError(f"Request to client could not be completed: {status_code}", verbosity=args.verbose)

    response = response.json()
    if response["success"] is False:
        logger.printError(f"Can't remove the API {token} {network} from the connector. Is not registered: {response}", verbosity=args.verbose)
        return

    payload = {
        "coin": token,
        "network": network,
    }
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        req = requests.post(
            url=f"http://localhost:{port}/admin/{REMOVE_CURRENCY}",
            json=payload,
            headers=headers
        )

        if args.verbose:
            logger.printInfo(f"Request sent to http://localhost:{port}/admin/{REMOVE_CURRENCY}: {req.json()}", verbosity=args.verbose)
        return req
    except Exception as e:
        logger.printError(f"Request to client could not be completed: {str(e)}", verbosity=args.verbose)
        return e


def updateApi(args, token, network, port):
    # Getting API information
    try:
        status_code, response = getApi(args, token, network, port)
    except Exception as e:
        logger.printError(f"Request to client could not be completed: {str(e)}", verbosity=args.verbose)

    # Check if API is not registered
    if status_code != 200:
        logger.printError(f"Request to client could not be completed: {status_code}", verbosity=args.verbose)

    response = response.json()
    if response["success"] is False:
        logger.printError(f"Can't update the API {token} {network} from the connector. Is not registered: {response}", verbosity=args.verbose)
        return

    configurable = utils.getTokenConfiguration(token, network)
    userData = []
    configurableData = []
    for configOption in configurable:
        if utils.queryYesNo(f"Do you want to update the {configOption}?"):
            configurableData.append(configOption)
            userData.append(utils.queryConfigurable(args, f"Please, introduce a value for {configOption}: ", configOption))

    config = dict(zip(configurableData, userData))
    payload = {
        "coin": token,
        "network": network,
        "config": config
    }

    headers = {
        'Content-Type': 'application/json'
    }
    try:
        req = requests.post(
            url=f"http://localhost:{port}/admin/{UPDATE_CURRENCY}",
            json=payload,
            headers=headers
        )

        if args.verbose:
            logger.printInfo(f"Request sent to http://localhost:{port}/admin/{UPDATE_CURRENCY}: {req.json()}", verbosity=args.verbose)
        return req
    except Exception as e:
        logger.printError(f"Request to client could not be completed: {str(e)}", verbosity=args.verbose)
        return e
