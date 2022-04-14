#!/bin/bash

if [ "${NETWORK}" = "regtest" -o "${NETWORK}" = "testnet" ]; then
  electrum_args="--${NETWORK} -v"
fi

if [ "${NETWORK}" = "regtest" ]; then
  Electrum/run_electrum --offline setconfig host "0.0.0.0" $electrum_args
fi

Electrum/run_electrum --offline setconfig rpchost "electrum-${NETWORK}" $electrum_args
Electrum/run_electrum --offline setconfig rpcuser "swapper" $electrum_args
Electrum/run_electrum --offline setconfig rpcpassword "swapper" $electrum_args
Electrum/run_electrum --offline setconfig rpcport "30000" $electrum_args
Electrum/run_electrum --offline setconfig oneserver "true" $electrum_args
Electrum/run_electrum --offline setconfig server $SERVER $electrum_args

Electrum/run_electrum daemon $electrum_args