#!/bin/bash

if [[ -n "${TESTNET}" ]]; then
  electrum_args="--testnet"
fi

Electrum/run_electrum --offline setconfig rpchost "electrum" $electrum_args
Electrum/run_electrum --offline setconfig rpcuser "swapper" $electrum_args
Electrum/run_electrum --offline setconfig rpcpassword "swapper" $electrum_args
Electrum/run_electrum --offline setconfig rpcport "30000" $electrum_args
Electrum/run_electrum --offline setconfig oneserver "true" $electrum_args
Electrum/run_electrum --offline setconfig server "electrumx:50001:t" $electrum_args

Electrum/run_electrum daemon $electrum_args