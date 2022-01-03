#!/usr/bin/python3
TOPIC_SEPARATOR = "/"
ADDRESS_BALANCE_TOPIC = "adressBalance"
NEW_BLOCKS_TOPIC = "newBlocks"


class Topic():

    def __init__(self, name, closingHandler=None):
        self.name = name
        self.closingHandler = closingHandler
