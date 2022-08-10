#!/bin/bash

# Checking parameters

supportedNetworks=("mainnet" "ropsten")


if [[ ! " ${supportedNetworks[@]} " =~ " ${NETWORK} " ]]; then
    echo "$NETWORK is not supported. Available networks are: ${supportedNetworks[@]}"
    exit 1
fi

if [[ -z ${HTTP_WEB3_PROVIDER} ]]; then
    echo "HTTP_WEB3_PROVIDER not specified. Please, specify execution node host. It can be HTTP provider or IPC provider if consensus and execution node run in the same machine"
    exit 1
fi

if [[ $HTTP_WEB3_PROVIDER == http* ]]; then

    if [[ -z ${JWT_TOKEN} ]]; then
        echo "JWT_TOKEN not set. It needs to be specified when HTTP provider is used"
        exit 1
    fi

    jwtSecret="--jwt-secret=${JWT_TOKEN}"
fi

if [[ -n ${RPC_HOST} ]]; then
    rpcHost="--rpc-host=${RPC_HOST}"
fi

if [[ -n ${RPC_PORT} ]]; then
    rpcPort="--rpc-port=${RPC_PORT}"
fi

if [[ -n ${GRPC_GATEWAY_HOST} ]]; then
    grpcGatewayHost="--grpc-gateway-host=${GRPC_GATEWAY_HOST}"
fi

if [[ -n ${GRPC_GATEWAY_PORT} ]]; then
    grpcGatewayPort="--grpc-gateway-port=${GRPC_GATEWAY_PORT}"
fi

if [[ -n ${DATA_DIR} ]]; then
    dataDir="--datadir=${DATA_DIR}"
fi

# Installing dependencies 
apt update && apt upgrade
apt install -y curl gnupg


# Download Prysm
declare -A versions=(
    [ropsten]=v2.1.4-rc.1
)

if [[ -n ${versions[$NETWORK]} ]]; then
    echo "Prysm version: ${versions[$NETWORK]}"
    export USE_PRYSM_VERSION=v2.1.4-rc.1
else
    echo "Using stable version of Prysm"
fi


mkdir prysm && cd prysm
curl https://raw.githubusercontent.com/prysmaticlabs/prysm/master/prysm.sh --output prysm.sh && chmod +x prysm.sh

# Download supported network genesis block

declare -A genesisBlocks=( 
    [ropsten]=https://github.com/eth-clients/merge-testnets/raw/main/ropsten-beacon-chain/genesis.ssz
)

if [[ -n ${genesisBlocks[$NETWORK]} ]]; then
    echo "Downloading genesis block from ${genesisBlocks[$NETWORK]}"
    cd /data && mkdir ${NETWORK} && cd ${NETWORK}
    curl -LJO ${genesisBlocks[$NETWORK]}
    genesisState="--genesis-state=/data/${NETWORK}/genesis.ssz"
fi

echo "Launching Prysm consensus node in network: $NETWORK"
cd /prysm
./prysm.sh beacon-chain \
    --accept-terms-of-use \
    --${NETWORK} \
    ${dataDir} \
    --http-web3provider=$HTTP_WEB3_PROVIDER \
    ${jwtSecret} \
    ${genesisState} \
    ${rpcHost} \
    ${rpcPort} \
    ${grpcGatewayHost} \
    ${grpcGatewayPort}