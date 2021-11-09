<h1 align="center">NodeChain</h1>

<p align="center">
  <a href="https://www.reddit.com/user/swapper_market"><b>Reddit</b></a> •
  <a href="https://bitcointalk.org/index.php?action=profile;u=3282789"><b>Bitcointalk</b></a> •
  <a href="https://ethereum.stackexchange.com/users/70542/swapper-market"><b>Ethereum StackExchange</b></a> •
  <a href="https://twitter.com/swapper_market"><b>Twitter</b></a> •
  <a href="https://medium.com/@swapper_market"><b>Medium</b></a> •
  <a href="https://docs.nodechain.swapper.market"><b>Docs</b></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0-blue"> 
  <img src="https://img.shields.io/badge/stability-experimental-orange"> 
</p>

<hr>

<b>Nodechain</b> is a service that allows you to create nodes on a blockchain and connect to them natively through the JSON-RPC protocol to its API.
In short, it allows the user to build and manage their own nodes natively without having to rely on external services.

This repository contains all the code related to the RPC and WS APIs, including the connection to the APIs of the native nodes of each blockchain.

<hr>

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.
See deployment for notes on how to deploy the project on a live system.

### Prerequisites

- [Docker](https://www.docker.com/get-started)
- [Docker-compose](https://docs.docker.com/compose/install/)
- [Python3](https://www.python.org/downloads/)
- [Pip](https://pypi.org/project/pip/)

## Running NodeChain

1. Follow the [CONTRIBUTING.md](https://github.com/swapper-org/NodeChain/blob/master/CONTRIBUTING.md) guidelines to clone
   the repository.

2. Navigate to `/scripts` and install the requirements:

```sh
~$ pip install -r "requirements.txt"
```

3. Run the script to build any API:

```sh
~$ python3 nodechain.py
```

4. Follow the steps of the script:
   - Choose an environment.
   - Choose an API to build.
   - Choose a port where you want to build the API.
   - Choose a path where you want to store the Blockchain.
   - Choose a port where you want to bind SSL port.
   - Choose if you want to add SSL to your node.

_(To activate SSL note that you need to have the files `swapper_cert.key` and `swapper_cert.crt` in the certificates directory)_

### Flags

You can also run NodeChain from command line without using the UI. You can get more information running:

```sh
~$ python3 nodechain.py -h
```

## Stop nodes

1. Navigate to `/scripts` and run the script to stop any running API:

```sh
~$ python3 nodechain.py
```

2. Choose the environment to show running nodes
3. Choose the API you want to stop.

## Usage

NodeChain uses the JSON RPC protocol for API requests. The API provides the following endpoints:

- `https://<URL-SERVER>:<PORT>/rpc` for RPC requests.
- `wss://<URL-SERVER>:<PORT>/ws` for real time requests.

## Environments

### Development stage

This environment is intended for the development and contribution of the project.
Blockchains used are created locally (_regtest, ganache,..._) facilitating the development and waiting times in block mining.

### Testnet stage

This environment is used to interact with any test network.

**_IMPORTANT: To work with full nodes in testnet mode, You need to have the blockchain synchronized for its use. If the testnet blockchain is not synchronized locally, some features might not work._**

### Mainnet stage

This environment is intended for real cases. You will be able to interact with any mainnet of any blockchain. Be aware that transactions may cost real fees if you use this environment.

**_IMPORTANT: You must use a different port for each API_**

## Contributing

Please read [Contribution Guidelines](https://github.com/swapper-org/NodeChain/blob/master/CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Docs

We use [Swagger](https://swagger.io/) for docs.
All the documentation concerning Nodechain is available at [NodeChain Docs](https://docs.nodechain.swapper.market)

All changes to the documentation must be made in the [NodeChain-docs](https://github.com/swapper-org/NodeChain-docs) repository.

## Version

Please read [Contribution Guidelines](https://github.com/swapper-org/NodeChain/blob/master/CONTRIBUTING.md) for details on our versioning system. For the version available, see the [tags on this repository](https://github.com/swapper-org/NodeChain/releases).

## License

This software is licensed under the MIT License. See [LICENSE](LICENSE) for the full details.

## Motivation and Vision

The main goal of the project is to give the user an easy way to be able to build their own blockchain nodes without external services, either in built on their own local machines or on production servers.
We believe in decentralizing the world and work to make it easily accessible to everyone.

## Related projects

- [Electrum](https://github.com/spesmilo/electrum)
- [ElectrumX](https://github.com/spesmilo/electrumx)
- [Electron Cash](https://github.com/Electron-Cash/Electron-Cash)
