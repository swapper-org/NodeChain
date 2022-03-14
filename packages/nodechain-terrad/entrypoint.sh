#!/bin/bash

terrad version --long | grep "version"
terrad init "terra-nodechain" --chain-id ${NET}

if [[ -n "${TESTNET}" ]]; then
  wget https://raw.githubusercontent.com/terra-money/testnet/master/${NET}/genesis.json && cp genesis.json ~/.terra/config/genesis.json
  wget https://raw.githubusercontent.com/terra-money/testnet/master/${NET}/addrbook.json -O ~/.terra/config/addrbook.json
  sed -i 's/minimum-gas-prices = "0uluna"/minimum-gas-prices = "0.01133uluna,0.15uusd,0.104938usdr,169.77ukrw,428.571umnt,0.125ueur,0.98ucny,16.37ujpy,0.11ugbp,10.88uinr,0.19ucad,0.14uchf,0.19uaud,0.2usgd,4.62uthb,1.25usek,1.25unok,0.9udkk,2180.0uidr,7.6uphp,1.17uhkd"/g' ~/.terra/config/app.toml
  sed -i 's/laddr = "tcp:\/\/127.0.0.1:26657"/laddr = "tcp:\/\/0.0.0.0:26657"/g' ~/.terra/config/config.toml
  sed -i '1,/enable = false/{s/enable = false/enable = true/g}' ~/.terra/config/app.toml
fi

if [[ -n "${MAINNET}" ]]; then
  wget https://columbus-genesis.s3.ap-northeast-1.amazonaws.com/${NET}-genesis.json && cp ${NET}-genesis.json ~/.terra/config/genesis.json
  wget https://network.terra.dev/addrbook.json -O ~/.terra/config/addrbook.json
  sed -i 's/minimum-gas-prices = "0uluna"/minimum-gas-prices = "0.01133uluna,0.15uusd,0.104938usdr,169.77ukrw,428.571umnt,0.125ueur,0.98ucny,16.37ujpy,0.11ugbp,10.88uinr,0.19ucad,0.14uchf,0.19uaud,0.2usgd,4.62uthb,1.25usek,1.25unok,0.9udkk,2180.0uidr,7.6uphp,1.17uhkd"/g' ~/.terra/config/app.toml
  sed -i 's/laddr = "tcp:\/\/127.0.0.1:26657"/laddr = "tcp:\/\/0.0.0.0:26657"/g' ~/.terra/config/config.toml
  sed -i '1,/enable = false/{s/enable = false/enable = true/g}' ~/.terra/config/app.toml
fi

terrad start