"""
    Testing NFT to NFT Exchange.
"""
from typing import Tuple
import pytest

from brownie import NFTToNFTExchange, FakeERC721, accounts
from brownie.network.contract import ProjectContract

@pytest.fixture
def exchange():
    """ Creating instance of NFTToNFTExchange. """
    return NFTToNFTExchange.deploy(600, {'from': accounts[0]})

@pytest.fixture
def create_tokens() -> Tuple[ProjectContract, ProjectContract]:
    """ Creating instances of FakerERC721.  """
    fake_erc721_1 = FakeERC721.deploy({'from': accounts[1]})
    fake_erc721_2 = FakeERC721.deploy({'from': accounts[2]})

    return (fake_erc721_1, fake_erc721_2)

@pytest.fixture
def mint_tokens(create_tokens) -> Tuple[str, str]:
    """ Distribution of tokens. """
    fake_erc721_1, fake_erc721_2 = create_tokens
    fake_erc721_1.mint(13424, accounts[3])
    fake_erc721_2.mint(25252, accounts[4])

    return (fake_erc721_1.address, fake_erc721_2.address)

def test_create_bid_and_check(exchange, mint_tokens) -> None:
    """ Creating a bid and check the result. """
    first_addr, second_addr = mint_tokens
    expected_bid_data = (
        1, 
        first_addr,
        second_addr,
        13423,
        25252,
        3000,
        False,
        False,
        False
    )
    
    tx = exchange.createBid(
        13423,
        first_addr,
        second_addr,
        25252,
        700,
        {'from': accounts[3], 'value': 3000}
    )
    
    bid = exchange.getTradeById(tx.return_value)
    
    assert bid == expected_bid_data