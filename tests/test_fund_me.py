import pytest
from brownie import accounts, network, exceptions
from scripts.deploy import deploy_fund_me
from scripts.utils import get_account, LOCAL_BLOCKCHAIN_ENV


def test_can_fund_and_withdraw():
    """
    Standard test on agnostic chain (will include deployment here just for the testing)

    Notes
    -----
    Where should I run my tests?
    1. Brownie Ganache Chain with Mocks: Always
    2. Testnet: Always (only for integration testing!)
    3. (Optional) Brownie mainnet-fork
    4. (Optional) Custom mainnet-fork (e.g., infura, alchemy)
    """
    # Arrange
    account = get_account()
    fund_me = deploy_fund_me()
    entrance_fee = fund_me.getEntranceFee()
    # Act (Fund)
    fund_txn = fund_me.fund({"from": account, "value": entrance_fee})
    fund_txn.wait(1)
    # Assert
    funded_value = fund_me.addressToAmountFunded(account.address)
    assert funded_value == entrance_fee
    # Act (Withdraw)
    withdraw_txn = fund_me.withdraw({"from": account})
    withdraw_txn.wait(1)
    # Assert (Withdraw)
    assert fund_me.addressToAmountFunded(account.address) == 0


def test_only_owner_can_withdraw():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip("Owner withdrawal test is for LOCAL testing only!")
    print("Withdrawal test ...")
    # Arrange
    fund_me = deploy_fund_me()
    print(f"The contract owner is: {fund_me.owner()}")
    # Act
    bad_actor = accounts[1]
    print(f"Test withdraw with bad actor: {bad_actor.address}")
    # Assert
    with pytest.raises(exceptions.VirtualMachineError):
        fund_me.withdraw({"from": bad_actor})
