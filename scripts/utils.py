from brownie import accounts, config, network, MockV3Aggregator
from web3 import Web3


DECIMALS = 8
STARTING_PRICE = 200000000000
# chain required for Mocking
LOCAL_BLOCKCHAIN_ENV = [
    "development",  # run using ganache-cli
    "ganache-local",  # ganache UI for mock contract deployment!
]
# chain required for Forking
FORKED_LOCAL_ENV = [
    "mainnet-fork",  # Ganache CLI, ethereum mainnet forked
]


def get_account():
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENV
        or network.show_active() in FORKED_LOCAL_ENV
    ):
        return accounts[0]
    else:
        return accounts.add(config["wallets"]["key_playground"])


def deploy_mock_v3_aggregator():
    """
    Deploy the Mock contract(s) in main/contracts/test/ directory, if required!

    Notes
    -----
    If the Ganache UI chain is deleted, all the contract would not be available!
    Proceed to reset the deployed contract instead by:
    1. Delete all the contracts in that chain id (e.g., 1337), build/deployments/1337
    2. Remove the chain_id data from the build/deployments/map.json
    """
    if len(MockV3Aggregator) <= 0:
        print(f"Active network is: {network.show_active()}! Deploying mocks ...")
        mock_aggregator = MockV3Aggregator.deploy(
            DECIMALS,
            STARTING_PRICE,  # the constructor input args
            {"from": get_account()},
        )
        print(f"Successfully deployed the mock: {mock_aggregator.address}!")
    else:
        print(f"Existing mock contract is found! Reusing: {MockV3Aggregator[-1]}")
