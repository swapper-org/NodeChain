<h1 align="center">NodeChain</h1>

<p align="center">
  <a href="https://www.reddit.com/r/SwapperDex"><b>Reddit</b></a> •
  <a href="https://twitter.com/SwapperDex"><b>Twitter</b></a> •
  <a href="https://medium.com/@SwapperDex"><b>Medium</b></a> •
  <a href="https://phoenix-7.gitbook.io/nodechain-en/"><b>Docs</b></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0-blue"> 
  <img src="https://img.shields.io/badge/stability-experimental-orange"> 
</p>

<hr>

<b>Nodechain</b> is a service that allows you to create nodes on a blockchain and connect to them natively through the JSON-RPC protocol to its API.
In short, it allows the user to build and manage their own nodes natively without having to rely on external services.

This repository contains all the code related to the RPC and WS APIs, including the connection to the APIs of the native nodes of each blockchain.

All the documentation related to the project can be found [here](https://phoenix-7.gitbook.io/nodechain-en/).

<hr>

## Getting Started
 
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 

### Prerequisites

- [Docker](https://www.docker.com/get-started)
- [Docker-compose](https://docs.docker.com/compose/install/)
- [Python3](https://www.python.org/downloads/)
- [Pip](https://pypi.org/project/pip/)

### Download the project

The first thing to do is to download the project from GitHub. To do this we will use the command-line. Follow the [CONTRIBUTING.md](https://github.com/swapper-org/NodeChain/blob/master/CONTRIBUTING.md) guidelines before cloning the repository.

```sh
$ git clone git@github.com:swapper-org/NodeChain.git
```

### Install dependencies

Depending on your setup, you will need to install the requirements.txt file dependencies if you have not installed them previously:
```sh
# Go to the scripts folder
$ cd scripts

# Install via pip
$ pip install -r "requirements.txt"
```

# Run NodeChain

You are ready to start your node. Just type:
```sh
$ python3 nodechain.py start

# or

$ ./nodechain.py start
```

### Flags

You can get more information about NodeChain:

```sh
~$ python3 nodechain.py -h
```

## Usage

NodeChain uses the JSON RPC protocol for API requests. The API provides the following endpoints:

- `https://<URL-SERVER>:<PORT>/<TOKEN>/<NETWORK>/rpc` for RPC requests.
- `wss://<URL-SERVER>:<PORT>/<TOKEN>/<NETWORK>/ws` for real time requests.

We also support REST API (HTTP)

- GET / POST `https://<URL-SERVER>:<PORT>/<TOKEN>/<NETWORK>/<METHOD>` for HTTP requests

More information can be founded [here](https://phoenix-7.gitbook.io/nodechain-en/reference/api-reference).

## Environments

### Regtest stage

This environment is intended for the development and contribution of the project.
Blockchains used are created locally (_regtest, ganache,..._) facilitating the development and waiting times in block mining.

### Testnet stage

This environment is used to interact with any test network.

**_IMPORTANT: To work with full nodes in testnet mode, You need to have the blockchain synchronized for its use. If the testnet blockchain is not synchronized locally, some features might not work._**

### Mainnet stage

This environment is intended for real cases. You will be able to interact with any mainnet of any blockchain. Be aware that transactions may cost real fees if you use this environment.

**_IMPORTANT: You must use a different port for each API_**

## Test

We use [Flake8](https://flake8.pycqa.org/en/latest/) for linting and [PyTest](https://docs.pytest.org/en/6.2.x/) for testing.

### Lint

The Flake8 configuration is inside the `.flake8` file. The project is configured only for linting python code from the `Connector/` and `scripts/` directories.

You can lint with the following command:

```sh
~$ flake8 --statistics
```

As optional, you can create a [GitHub Hook](https://docs.github.com/en/developers/webhooks-and-events/webhooks/about-webhooks) to automatically check that your code follows the linting rules before commiting your changes.

You can find the tutorial to lint automatically with hooks [here](https://phoenix-7.gitbook.io/nodechain-en/develop/how-to/lint-automatically-with-hooks).

### Local testing

Do you need to test your changes without download the whole blockchain?. Follow the [tutorial](https://phoenix-7.gitbook.io/nodechain-en/develop/how-to/run-tests-locally) and help to improve NodeChain!

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

We use GitBook for docs.
All the documentation concerning Nodechain is available at [NodeChain Docs](https://phoenix-7.gitbook.io/nodechain-en)

All changes to the RPC/WS documentation must be made in the [NodeChain-docs](https://github.com/swapper-org/NodeChain-docs) repository.

## Version

Please read [Contribution Guidelines](https://github.com/swapper-org/NodeChain/blob/master/CONTRIBUTING.md) for details on our versioning system. For the version available, see the [tags on this repository](https://github.com/swapper-org/NodeChain/releases).

## License

This software is licensed under the MIT License. See [LICENSE](LICENSE) for the full details.

## Motivation and Vision

The main goal of the project is to give the user an easy way to be able to build their own blockchain nodes without external services, either inbuilt on their own local machines or on production servers.

In developing NodeChain we seek to incorporate purely native services and protocols, avoiding unofficial dependencies.

**We believe in decentralizing the world and work to make it easily accessible to everyone.**

NodeChain is a project by the community and for the community. We stand firm in the context of collaboration by growing the Blockchain ecosystem and enabling the scalability of projects in a simple way.

Growing the ecosystem around NodeChain is an arduous but necessary task. For this reason, we thank all the contributors who give part of their time.

## Related projects

Thanks to every project that make NodeChain possible. You can see the list [here](https://phoenix-7.gitbook.io/nodechain-en/learn/ecosystem/acknowledgments).
