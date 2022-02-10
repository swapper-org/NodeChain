#!/bin/sh
set -e

if [ $(echo "$1" | cut -c1) = "-" ]; then
  echo "$0: assuming arguments for bitcoind"

  set -- bitcoind "$@"
fi

if [ $(echo "$1" | cut -c1) = "-" ] || [ "$1" = "bitcoind" ]; then
  mkdir -p "$BITCOIN_DATA"
  chmod 700 "$BITCOIN_DATA"
  chown -R bitcoin "$BITCOIN_DATA"

  echo "$0: setting data directory to $BITCOIN_DATA"

  set -- "$@" -datadir="$BITCOIN_DATA"
fi

if [ "$1" = "bitcoind" ] || [ "$1" = "bitcoin-cli" ] || [ "$1" = "bitcoin-tx" ]; then
  echo
  if [ "${NETWORK}" = "regtest" ]; then
    WALLETDIR="$BITCOIN_DATA/regtest"
  elif [ "${NETWORK}" = "testnet" ]; then
    WALLETDIR="$BITCOIN_DATA/testnet3"
  elif [ "${NETWORK}" = "mainnet" ]; then
    WALLETDIR="$BITCOIN_DATA/mainnet"
  fi
  
  WALLETFILE="${WALLETDIR}/wallet.dat"
  mkdir -p "${WALLETDIR}"
  chown -R bitcoin:bitcoin "${WALLETDIR}"
  if ! [ -f "${WALLETFILE}" ]; then
    echo "The wallet does not exists, creating it at ${WALLETDIR}..."
    gosu bitcoin bitcoin-wallet "-wallet=" create
  fi
  exec gosu bitcoin "$@"
fi

echo
exec "$@"