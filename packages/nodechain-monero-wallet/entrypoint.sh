#!/bin/sh
set -e

if [ $(echo "$1" | cut -c1) = "-" ]; then
  echo "$0: assuming arguments for monero-wallet-rpc"

  set -- monero-wallet-rpc "$@"
fi

if [ $(echo "$1" | cut -c1) = "-" ] || [ "$1" = "monero-wallet-rpc" ]; then

  echo "$0: cleaning wallets in $MONERO_DATA"

  rm -rf "$MONERO_DATA/wallet-dir"

  echo "$0: setting directory $MONERO_DATA"

  mkdir -p "$MONERO_DATA"
  mv "./wallet-dir" "$MONERO_DATA/wallet-dir"
  chmod 700 "$MONERO_DATA"
  chown -R monero "$MONERO_DATA"

  echo "$0: setting data directory to $MONERO_DATA"

  set -- "$@" --wallet-dir="$MONERO_DATA/wallet-dir" --log-file="$MONERO_DATA/debug.log" # --config-file="$MONERO_DATA/monero-wallet-cli.conf"
fi

echo
exec "$@"