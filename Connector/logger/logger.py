#!/usr/bin/python3
import os
import logging

loggingModes = {
    1: logging.DEBUG,
    2: logging.INFO,
    3: logging.WARNING,
    4: logging.ERROR,
    5: logging.CRITICAL
}

DEFAULT_MODE = 2

mode = os.environ.get("verbose", DEFAULT_MODE)

format = '[%(levelname)s] [%(asctime)s] %(message)s'
dateFormat = '%H:%M:%S %d-%m-%Y'


logging.basicConfig(
    level=loggingModes[mode],
    format=format,
    datefmt=dateFormat
)


class Logger:

    @staticmethod
    def printInfo(msg: str):
        logging.info(msg)

    @staticmethod
    def printWarning(msg: str):
        logging.warning(msg)

    @staticmethod
    def printError(msg: str):
        logging.error(msg)

    @staticmethod
    def printDebug(msg: str):
        logging.debug(msg)

    @staticmethod
    def printCritical(msg: str, exc_info: bool = True):
        logging.critical(msg, exc_info=exc_info)
