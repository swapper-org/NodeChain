#!/usr/bin/python3
from .constants import *
import os
from logger import logger


ADDRESSES_SUBSCRIBED = {}
COIN = os.environ["COIN"]


class SubcriptionsHandler():


    @staticmethod
    def subscribe(address, client):
        
        logger.printInfo(f"Client trying to subscribe to address {address}")
        if COIN not in ADDRESSES_SUBSCRIBED:
            logger.printInfo(f"Creating subscriptions for {COIN}")
            ADDRESSES_SUBSCRIBED[COIN] = {}

        addressesByCoin = ADDRESSES_SUBSCRIBED[COIN]

        if address not in addressesByCoin:
            addressesByCoin[address] = []
            addressesByCoin[address].append(client)
            client.addAddress(address)
            
            logger.printInfo(f"Client successfully subscribed to address ${address}")

            return {
                SUBSCRIBED: True
            }

        elif client not in addressesByCoin[address]:
            addressesByCoin[address].append(client)
            client.addAddress(address)

            logger.printInfo(f"Client successfully subscribed to address ${address}")
    
            return {
                SUBSCRIBED: True
            }
        
        logger.printInfo(f"Client already subscribed to address ${address}")

        return {
            SUBSCRIBED: False
        }


    @staticmethod
    def unsubscribe(address, client):

        if COIN not in ADDRESSES_SUBSCRIBED:
            logger.printError(f"Coin doesn't exist in subscription handler: {COIN}")
            return {
                UNSUBSCRIBED: False
            }

        addressesByCoin = ADDRESSES_SUBSCRIBED[COIN]

        if address not in addressesByCoin:
            logger.printError(f"Address {address} doesn't exist for {COIN} in subscription handler")
            return {
                UNSUBSCRIBED: False
            }

        if client not in addressesByCoin[address]:
            logger.printError(f"Client is not subscribed to address {address}")
            return {
                UNSUBSCRIBED: False
            }

        addressesByCoin[address].remove(client)
        client.removeAddress(address)

        SubcriptionsHandler.clean(addressesByCoin, address)

        logger.printInfo(f"Client successfully unsubscribed to address {address}")
        return {
            UNSUBSCRIBED: True
        }


    @staticmethod
    def removeClient(client):

        if COIN not in ADDRESSES_SUBSCRIBED:
            logger.printError(f"{COIN} doesn't exit in subscriptions handler")
            return

        addressesByCoin = ADDRESSES_SUBSCRIBED[COIN]

        for addressSubscribed in client.subscriptions:
            if addressSubscribed in addressesByCoin:
                if client in addressesByCoin[addressSubscribed]:
                    addressesByCoin[addressSubscribed].remove(client)
                    SubcriptionsHandler.clean(addressesByCoin, addressSubscribed)

        logger.printInfo("Client removed successfully from subscriptions handler")
        client.clean()
        return


    @staticmethod
    def clean(addressesByCoin, address):

        if not addressesByCoin[address]:
            addressesByCoin.pop(address, None)
            if not ADDRESSES_SUBSCRIBED[COIN]:
                ADDRESSES_SUBSCRIBED.pop(COIN, None)

        return


    @staticmethod
    def coinInAddressSubscription():
        return COIN in ADDRESSES_SUBSCRIBED
    

    @staticmethod
    def getSubscriptionsAvailable():
        return ADDRESSES_SUBSCRIBED[COIN]
    

    @staticmethod
    def getAddressClients(address):

        if SubcriptionsHandler.coinInAddressSubscription() and SubcriptionsHandler.addressHasClients(address):
            return ADDRESSES_SUBSCRIBED[COIN][address]
        
        return []
    

    @staticmethod
    def addressHasClients(address):
        if COIN in ADDRESSES_SUBSCRIBED:
            return address in ADDRESSES_SUBSCRIBED[COIN]
        return False