#!/usr/bin/python3
import sys
import os
import json
import requests
import logger
import utils

ADD_COIN = "addcoin"
GET_COIN = "getcoin"
UPDATE_COIN = "updatecoin"
REMOVE_COIN = "removecoin"


def addApi(args, token, network, port, defaultConfig=True):
    # Get if API is registered
    try:
        status_code, response = getApi(args, token, network, port)
    except Exception as e:
        logger.printError(f"Request to client could not be completed: {str(e)}", verbosity=args.verbose)

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
    try:
        req = requests.post(
            url=f"http://localhost:{port}/admin/{ADD_COIN}",
            json=payload,
            headers=headers
        )

        if args.verbose:
            logger.printInfo(f"Request sended to http://localhost:{port}/admin/{ADD_COIN}: {req.json()}", verbosity=args.verbose)
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
            url=f"http://localhost:{port}/admin/{GET_COIN}",
            json=payload,
            headers=headers
        )

        if args.verbose:
            logger.printInfo(f"Request sended to http://localhost:{port}/admin/{GET_COIN}: {req.json()}", verbosity=args.verbose)
        return req.status_code, req
    except Exception as e:
        logger.printError(f"Request to client could not be completed: {str(e)}", verbosity=args.verbose)
        return e
