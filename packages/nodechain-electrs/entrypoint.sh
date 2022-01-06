#!/bin/bash

if [[ -n "${TESTNET}" ]]; then
  electrs_args="--network testnet"
fi

if [ $(echo "$1" | cut -c1) = "-" ]; then
  echo "$0: assuming arguments for electrs"

  set -- electrs "$@"
fi

if [ $(echo "$1" | cut -c1) = "-" ] || [ "$1" = "electrs" ]; then

  echo "$0: setting script as command"
  ln -s "${ELECTRS_COMMAND}" "/usr/local/bin/electrs"

  mkdir -p "$ELECTRS_DATA"
  chmod 700 "$ELECTRS_DATA"

  echo "$0: setting data directory to $ELECTRS_DATA"

  set -- "$@" --db-dir="$ELECTRS_DATA" --daemon-dir="$BITCOIN_DATA" --daemon-rpc-addr="${DAEMON_RPC_URL}" --cookie="swapper:swapper" --electrum-rpc-addr="${ELECTRUM_RPC_URL}" $electrs_args
fi

echo
exec "$@"