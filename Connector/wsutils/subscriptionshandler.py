#!/usr/bin/python3
from .constants import *
import os

ADDRESSES_SUBSCRIBED = {}
COIN = os.environ["COIN"]


class SubcriptionsHandler():


    @staticmethod
    def subscribe(address, client):
        
        if COIN not in ADDRESSES_SUBSCRIBED:
            ADDRESSES_SUBSCRIBED[COIN] = {}

        addressesByCoin = ADDRESSES_SUBSCRIBED[COIN]

        if address not in addressesByCoin:
            addressesByCoin[address] = []
            addressesByCoin[address].append(client)
            client.addAddress(address)
            return {
                SUBSCRIBED: True
            }
        elif client not in addressesByCoin[address]:
            addressesByCoin[address].append(client)
            client.addAddress(address)
            return {
                SUBSCRIBED: True
            }
        return {
            SUBSCRIBED: False
        }


    @staticmethod
    def unsubscribe(address, client):
        if COIN not in ADDRESSES_SUBSCRIBED:
            print("Coin doesn't exists: ", COIN)
            return {
                UNSUBSCRIBED: False
            }

        addressesByCoin = ADDRESSES_SUBSCRIBED[COIN]

        if address not in addressesByCoin:
            print("Address doesn't exists for that coin")
            return {
                UNSUBSCRIBED: False
            }

        if client not in addressesByCoin[address]:
            print("Client doesn't exists for that address")
            return {
                UNSUBSCRIBED: False
            }

        addressesByCoin[address].remove(client)
        client.removeAddress(address)

        SubcriptionsHandler.clean(addressesByCoin, address)

        return {
            UNSUBSCRIBED: True
        }


    @staticmethod
    def removeClient(client):

        if COIN not in ADDRESSES_SUBSCRIBED:
            print("Coin doesn't exists: ", COIN)
            return

        addressesByCoin = ADDRESSES_SUBSCRIBED[COIN]

        for addressSubscribed in client.subscriptions:
            if addressSubscribed in addressesByCoin:
                if client in addressesByCoin[addressSubscribed]:
                    addressesByCoin[addressSubscribed].remove(client)
                    SubcriptionsHandler.clean(addressesByCoin, addressSubscribed)

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