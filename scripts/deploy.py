from brownie import config, network, FundMe, MockV3Aggregator
from .utils import get_account, deploy_mock_v3_aggregator, LOCAL_BLOCKCHAIN_ENV
from web3 import Web3


def deploy_fund_me():
    """
    Deploy the FundMe contract

    Notes
    -----
    The following network run will use:
    1. --development    : MOCK price feed. No archive
    2. --ganache-local  : MOCK price feed, archived deployment (chainId: 1337)
    3. --mainnet-fork   : FORK price feed from mainnet on brownie Ganache CLI. No archive
    4. --sepolia        : Normal run on persistent chain (chainId: 11155111)
    """
    # get account to use
    account = get_account()
    print(f"Run on '{network.show_active()}' with address: {account}")
    network_id = network.show_active()

    # handle data feed address
    if network_id in LOCAL_BLOCKCHAIN_ENV:
        deploy_mock_v3_aggregator()  # Mocking the oracle
        data_feed_address = MockV3Aggregator[-1].address
    else:
        data_feed_address = config["networks"][network_id]["eth_usd_price_feed"]

    # deploy contract here
    fund_me = FundMe.deploy(
        data_feed_address,  # the contract's constructor input
        {"from": account},
        publish_source=config["networks"].get(network_id, {}).get("verify", False),
    )
    # publish source code to the EXPLORER for contract verification
    print(f"Deployed contract address: {fund_me}")
    print(f"Current ETH/USD price: {fund_me.getPrice() / (10**8)}")  # sanity checking

    # How to run on local/Ganache? Need to "deploy" the chainlink oracle to local also:
    # 1. Mocking (deploying a "fake" oracle chainlink on local)
    # 2. Forking
    return fund_me


def main():
    print("____ Begin deploying FundMe contract ...")
    deploy_fund_me()
    print("____ Contract is deployed!")
