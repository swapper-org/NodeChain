#!/bin/sh
set -e

if [ $(echo "$1" | cut -c1) = "-" ]; then
  echo "$0: assuming arguments for monerod"

  set -- monerod "$@"
fi

if [ $(echo "$1" | cut -c1) = "-" ] || [ "$1" = "monerod" ]; then
  mkdir -p "$MONERO_DATA"
  chmod 700 "$MONERO_DATA"
  chown -R monero "$MONERO_DATA"

  echo "$0: setting data directory to $MONERO_DATA"

  set -- "$@" --data-dir="$MONERO_DATA" # --non-interactive --config-file="$MONERO_DATA/monerod.conf"
fi

echo
exec "$@"