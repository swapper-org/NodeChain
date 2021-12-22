#!/bin/sh
set -e

if [ $(echo "$1" | cut -c1) = "-" ]; then
  echo "$0: assuming arguments for monero-wallet-rpc"

  set -- monero-wallet-rpc "$@"
fi


if [ $(echo "$1" | cut -c1) = "-" ] || [ "$1" = "monero-wallet-rpc" ]; then
  mkdir -p "$MONERO_DATA"
  chmod 700 "$MONERO_DATA"
  chown -R monero "$MONERO_DATA"
  mv swapper "$MONERO_DATA/swapper"
  mv swapper.keys "$MONERO_DATA/swapper.keys"

  echo "$0: setting data directory to $MONERO_DATA"

  set -- "$@" --log-file="$MONERO_DATA/debug.log" --wallet-file="$MONERO_DATA/swapper" --password="swapper"
fi

echo
exec "$@"