"""
    Testing NFT to NFT Exchange.
"""
from time import time
from collections import OrderedDict
from typing import Tuple
import pytest

from brownie import NFTToNFTExchange, FakeERC721, accounts, reverts
from brownie.network.contract import ProjectContract
from brownie.network.transaction import TransactionReceipt

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

    """
        Trade Id
        Bidder NFT Address
        Asker NFT Address
        Bidder NFT Id
        Asker NFT Id
        Price
        Bidder Recieve NFT
        Asker Receive NFT
        Asker Receive NFT
    """
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

    tx: TransactionReceipt = exchange.createBid(
        13423,
        first_addr,
        second_addr,
        25252,
        700,
        {'from': accounts[3], 'value': 3000}
    )
    
    bid = exchange.getTradeById(tx.return_value)
    
    assert bid == expected_bid_data

def test_create_bid_and_check_events(exchange, mint_tokens) -> None:
    """ Creating a bid and check the emitted events. """
    first_addr, second_addr = mint_tokens
    
    events: OrderedDict = exchange.createBid(
        13423,
        first_addr,
        second_addr,
        25252,
        700,
        {'from': accounts[3], 'value': 3000}
    ).events
    # Check if the event was called.
    assert events.keys()[0] == 'BidCreated'
    # Check events items.
    event_items = events['BidCreated']
    assert 1 == event_items['TradeId']
    assert accounts[3] == event_items['creator']
    assert accounts[3] == event_items['bidderAddress']
    assert first_addr == event_items['bidderNFTAddress']
    assert second_addr == event_items['askerNFTAddress']
    assert 13423 == event_items['bidderNFTId']
    assert 3000 == event_items['price']
    assert int(time() + 700) == event_items['expirestAt']

def test_create_bid_with_the_equal_nft_id(exchange, mint_tokens) -> None:
    """ Create a bid with the same nft id and check the return message. """
    first_addr, second_addr = mint_tokens

    with reverts('NFT cannot be the same!'):
        tx = exchange.createBid(
            13423,
            first_addr,
            first_addr,
            13423,
            700,
            {'from': accounts[3], 'value': 3000}
        )

def test_for_creating_a_bid_with_a_duration_that_is_less_than_the_minimum(
    exchange, mint_tokens) -> None:
    """ Create a bid with duration < min_duration. """
    first_addr, second_addr = mint_tokens

    with reverts("The duration value cannot be less than the minimum duration value!"):
        exchange.createBid(
            13423,
            first_addr,
            second_addr,
            25252,
            500,
            {'from': accounts[3], 'value': 3000}
        )

def test_create_ask_and_check(exchange, mint_tokens) -> None:
    """ Create a ask and check the result. """
    first_addr, second_addr = mint_tokens

    """
        Trade Id
        Bidder NFT Address
        Asker NFT Address
        Bidder NFT Id
        Asker NFT Id
        Price
        Bidder Recieve NFT
        Asker Receive NFT
        Asker Receive NFT
    """
    expected_ask_data = (
        1,                  
        first_addr,         
        second_addr,   
        25252,
        13423,
        4000,
        False,
        False,
        False
    )

    tx: TransactionReceipt = exchange.createAsk(
        13423,
        25252,
        first_addr,
        second_addr,        
        700,
        4000,
        {'from': accounts[4]}
    )

    ask = exchange.getTradeById(tx.return_value)

    assert expected_ask_data == ask