from brownie.network.contract import ContractContainer
import pytest

from brownie import accounts

pytest.fixture
def exchange():
    return accounts[0].deploy()