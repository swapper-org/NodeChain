#!/bin/bash

if [[ -n "${TESTNET}" ]]; then
  electron_args="--testnet"
fi

Electron-Cash/electron-cash setconfig rpchost "electrum-${NETWORK}" $electron_args
Electron-Cash/electron-cash setconfig rpcuser "swapper" $electron_args
Electron-Cash/electron-cash setconfig rpcpassword "swapper" $electron_args
Electron-Cash/electron-cash setconfig rpcport "30000" $electron_args
Electron-Cash/electron-cash setconfig oneserver "true" $electron_args
Electron-Cash/electron-cash setconfig server "electrumx-${NETWORK}:50001:t" $electron_args

Electron-Cash/electron-cash daemon $electron_args