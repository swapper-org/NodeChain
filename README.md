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


### Development stage
This environment is intended for the development and contribution of the project.
Blockchains used are created locally (*regtest, ganache,...*) facilitating the development and waiting times in block mining.

1. Follow the [CONTRIBUTING.md](https://github.com/swapper-org/NodeChain/blob/master/CONTRIBUTING.md) guidelines to clone
the repository.

2. Navigate to `/scripts` and install the requirements:
```sh
~$ pip install -r "requirements.txt"
```

3. Run the script to build any API:
```sh
~$ python3 buildapi.py
```

4. Follow the steps of the script:
   - Choose "Development" environment.
   - Choose an API to build.
   - Choose a port where you want to build the API.
   - Choose a path where you want to store the Blockchain.
   - Choose a port where you want to bind SSL port.
   - Choose if you want to add SSL to your node. 

_(To activate SSL note that you need to have the files `swapper_cert.key` and `swapper_cert.crt` in the certificates directory)_


## Deployment

### Testnet stage

**_IMPORTANT: To work with full nodes in development mode, You need to have the blockchain synchronized for its use. If the testnet blockchain is not synchronized locally, some features might not work._**

1. Clone the project in your computer or your server

```sh
~$ git clone https://github.com/swappermarket/NodeChain.git
```

2. Navigate to `/scripts` and install the requirements:

```sh
~$ pip install -r "requirements.txt"
```

3. Run the script to build any API:
```sh
~$ python3 buildapi.py
```

4. Follow the steps of the script:
    - Choose "Testnet" environment.
    - Choose an API to build
    - Choose a port where you want to build the API
    - Choose a path where you want to store the Blockchain
    - Choose a port where you want to bind SSL port
    - Choose if you want to add SSL to your node.

_(To activate SSL note that you need to have the files `swapper_cert.key` and `swapper_cert.crt` in the certificates directory)_


### Mainnet stage

1. Clone the project in your computer or your server

```sh
~$ git clone https://github.com/swappermarket/NodeChain.git
```

2. Navigate to `/scripts` and install the requirements:

```sh
~$ pip install -r "requirements.txt"
```

3. Run the script to build any API:
```sh
~$ python3 buildapi.py
```

4. Follow the steps of the script:
    - Choose "Mainnet" environment.
    - Choose an API to build
    - Choose a port where you want to build the API
    - Choose a path where you want to store the Blockchain
    - Choose a port where you want to bind SSL port
    - Choose if you want to add SSL to your node.

_(To activate SSL note that you need to have the files `swapper_cert.key` and `swapper_cert.crt` in the certificates directory)_

**IMPORTANT: You must use a different port for each API**

## Stop nodes

1. Navigate to `/scripts` and run the script to stop any running API:
```sh
~$ python3 buildapi.py
```
2. Choose the environment to show running nodes
3. Choose the API you want to stop.

## Usage
NodeChain uses the JSON RPC protocol for API requests. The API provides the following endpoints:
- `https://<URL-SERVER>:<PORT>/rpc` for RPC requests.
- `wss://<URL-SERVER>:<PORT>/ws` for real time requests.

## Test


We use [Flake8](https://flake8.pycqa.org/en/latest/) for linting and [PyTest](https://docs.pytest.org/en/6.2.x/) for testing.

### Lint

The Flake8 configuration is inside the `.flake8` file. The project is configured only for linting python code from the `Connector/` and `scripts/` directories.

You can lint with the following command:

```sh
~$ flake8 --statistics
```

As optional, you can create a [GitHub Hook](https://docs.github.com/en/developers/webhooks-and-events/webhooks/about-webhooks) to automatically check that your code follows the linting rules before commiting your changes.

Follow the steps to create a pre-commit hook

1. Create the file `pre-commit` inside the path `.git/hooks/` of your local repository with this content:

```sh
#!/bin/bash

ROOT_DIR="$(git rev-parse --show-toplevel)"

echo "Running Flake8"
flake8 ${ROOT_DIR} --statistics
```

2. Assign it execution permission

```sh
~$ chmod +x .git/hooks/pre-commit

```

### Local testing

You can do the local testing manually:

1. Lint the project using the instructions above.

2. Use the `scripts/buildapi.py` script to launch NodeChain in development network locally and select the token you want to test
 
3. Run tests inside the Connector docker image with the following command where you have to replace ${TOKEN} by the token symbol you are testing in lower case 
 
```sh
docker exec -it ${TOKEN}_development_api_connector_1 bash -c "cd Connector && python -m pytest -c tests/${TOKEN}/pytest_${TOKEN}.ini -s --cov=${TOKEN}/ --cov=logger/ --cov=rpcutils/ --cov=wsutils/ tests/${TOKEN}"
```

### CircleCI testing

If you have a [CircleCI](https://circleci.com/) account, you can use it for remote testing. Use the GitHub account with your forked Nodechain repository.

Follow the steps for CircleCI remote testing

1. Go to the projects tab and click on the _Set Up Project_ button of your forked Nodechain repository.
2. Select the _staging_ branch
3. Implement your fix or feature
4. Push the code to GitHub and tests will be automatically executed

_**Note**: When running test remotely, CircleCI will execute all the jobs defined in the `.circleci/config.yml`_


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