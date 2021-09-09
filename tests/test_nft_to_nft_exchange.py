"""
    Testing NFT to NFT Exchange.
"""
from time import time
from collections import OrderedDict
from typing import Tuple
import pytest

from brownie.network.contract import ProjectContract
from brownie.network.transaction import TransactionReceipt
from brownie import NFTToNFTExchange, FakeERC721, accounts, reverts, chain

@pytest.fixture
def exchange() -> ProjectContract:
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
        Bidder Address
        Asker Address
        Creator Address
        Paid
        Bidder NFT Id
        Asker NFT Id
        Price
    """
    expected_bid_data = (
        1, 
        first_addr,
        second_addr,
        accounts[3],
        "0x0000000000000000000000000000000000000000",
        accounts[3],
        False,
        13423,
        25252,
        3000
    )

    tx: TransactionReceipt = exchange.createBid(
        13423,
        25252,
        first_addr,
        second_addr,
        700,
        3000,
        {'from': accounts[3]}
    )
    
    bid = exchange.getTradeById(tx.return_value)
    
    assert bid == expected_bid_data

def test_create_bid_and_check_events(exchange, mint_tokens) -> None:
    """ Creating a bid and check the emitted events. """
    first_addr, second_addr = mint_tokens
    
    events: OrderedDict = exchange.createBid(
        13423,
        25252,
        first_addr,
        second_addr,
        700,
        3000,
        {'from': accounts[3]}
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
    assert 25252 == event_items['askerNFTId']
    assert 3000 == event_items['price']
    assert int(time() + 700) == event_items['expirestAt']

def test_create_bid_with_the_equal_nft_id(exchange, mint_tokens) -> None:
    """ Create a bid with the same nft id and check revert. """
    first_addr, second_addr = mint_tokens

    with reverts('NFT cannot be the same!'):
        tx = exchange.createBid(
            13423,
            13423,
            first_addr,
            first_addr,
            700,
            3000,
            {'from': accounts[3]}
        )

def test_for_creating_a_bid_with_a_duration_that_is_less_than_the_minimum(
    exchange, mint_tokens) -> None:
    """ Create a bid with duration < min_duration. """
    first_addr, second_addr = mint_tokens

    with reverts("The duration value cannot be less than the minimum duration value!"):
        exchange.createBid(
            13423,
            25252,
            first_addr,
            second_addr,
            500,
            3000,
            {'from': accounts[3]}
        )

def test_create_ask_and_check(exchange, mint_tokens) -> None:
    """ Create a ask and check the result. """
    first_addr, second_addr = mint_tokens

    """
        Trade Id
        Bidder NFT Address
        Asker NFT Address
        Bidder Address
        Asker Address
        Creator Address
        Paid
        Bidder NFT Id
        Asker NFT Id
        Price
    """
    expected_ask_data = (
        1,                  
        first_addr,         
        second_addr, 
        "0x0000000000000000000000000000000000000000",
        accounts[4],
        accounts[4],  
        13423,
        25252,
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

def test_create_ask_and_check(exchange, mint_tokens) -> None:
    """ Creating a ask and check the emitted events. """
    first_addr, second_addr = mint_tokens

    events: OrderedDict = exchange.createAsk(
        13423,
        25252,
        first_addr,
        second_addr,        
        700,
        4000,
        {'from': accounts[4]}
    ).events
    # Check if the event was called.
    assert events.keys()[0] == 'AskCreated'
    # Check events items.
    event_items = events['AskCreated']
    assert 1 == event_items['TradeId']
    assert accounts[4] == event_items['creator']
    assert accounts[4] == event_items['askerAddress']
    assert first_addr == event_items['bidderNFTAddress']
    assert second_addr == event_items['askerNFTAddress']
    assert 25252 == event_items['askerNFTId']
    assert 13423 == event_items['bidderNFTId']
    assert 4000 == event_items['price']
    assert int(time() + 700) == event_items['expirestAt']

def test_create_ask_with_the_equal_nft(exchange, mint_tokens) -> None:
    """ Create a ask with the same nft id and check revert. """
    first_addr, second_addr = mint_tokens

    with reverts('NFT cannot be the same!'):
        tx = exchange.createAsk(
            13423,
            13423,
            first_addr,
            first_addr,
            700,
            4000,
            {'from': accounts[4]}
        )

def test_for_creating_a_ask_with_a_duration_that_is_less_than_the_minimum(
    exchange, mint_tokens) -> None:
    """ Create a ask with duration < min_duration and check revert. """
    first_addr, second_addr = mint_tokens

    with reverts("The duration value cannot be less than the minimum duration value!"):
        exchange.createAsk(
            13423,
            25252,
            first_addr,
            second_addr,
            500,
            4000,
            {'from': accounts[4]}
        )

def test_stake_asker_nft_for_bid_and_check(exchange, create_tokens) -> None:
    """ Put NFT and check the changes in the internal memory. """
    first_fake_token, second_fake_token = create_tokens
    first_fake_token.mint(13424, accounts[3])
    second_fake_token.mint(25252, accounts[4])
    
    # Create bid.
    create_bid_tx: TransactionReceipt = exchange.createBid(
        13424,
        25252,
        first_fake_token.address,
        second_fake_token.address,
        700,
        3000,
        {'from': accounts[3]}
    )
    # Stake asker NFT.
    second_fake_token.approve(exchange.address, 25252, {'from': accounts[4]})
    exchange.stakeNft(create_bid_tx.return_value, 25252, {'from': accounts[4]})
    # Get trade.
    bid: OrderedDict = exchange.getTradeById(create_bid_tx.return_value)

    assert exchange.address == second_fake_token.ownerOf(25252)
    # Check asker.
    assert bid[4] == accounts[4]
    # Check paid flag.
    assert bid[6] == False

def test_stake_asker_nft_for_a_nonexist_bid_and_check(exchange) -> None:
    with reverts("Trade does not exist!"):    
        exchange.stakeNft(1, 25252, {'from': accounts[4]})

def test_stake_asker_nft_for_expired_bid_and_check(exchange, mint_tokens) -> None:
    """ Put NFT for expired bid and check revert. """
    first_addr, second_adddr = mint_tokens
    
    # Create bid.
    create_bid_tx: TransactionReceipt = exchange.createBid(
        13424,
        25252,
        first_addr,
        second_adddr,
        700,
        3000,
        {'from': accounts[3]}
    )
    # Time travel. 
    chain.sleep(800)
    with reverts("The timestamp of the trade must be less than the block timestamp value!"):
        exchange.stakeNft(create_bid_tx.return_value, 25252, {'from': accounts[4]})

def test_stake_another_nft_for_bid_and_check(exchange, mint_tokens) -> None:
    """ Put another NFT and check revert. """
    first_addr, second_adddr = mint_tokens
    
    # Create bid.
    create_bid_tx: TransactionReceipt = exchange.createBid(
        13424,
        25252,
        first_addr,
        second_adddr,
        700,
        3000,
        {'from': accounts[3]}
    )
    with reverts("The NFT identifier is not the seller's NFT or the buyer's NFT!"):
        exchange.stakeNft(create_bid_tx.return_value, 11111, {'from': accounts[4]})

def test_stake_bidder_nft_for_ask_and_check(exchange, create_tokens) -> None:
    """ Put NFT and check the changes in the internal memory. """
    first_fake_token, second_fake_token = create_tokens
    first_fake_token.mint(13424, accounts[3])
    second_fake_token.mint(25252, accounts[4])
    
    # Create ask.
    create_bid_tx: TransactionReceipt = exchange.createAsk(
        13424,
        25252,
        first_fake_token.address,
        second_fake_token.address,
        4000,
        700,
        {'from': accounts[4]}
    )
    # Stake asker NFT.
    first_fake_token.approve(exchange.address, 13424, {'from': accounts[3]})
    exchange.stakeNft(create_bid_tx.return_value, 13424, {'from': accounts[3]})
    # Get trade.
    bid: OrderedDict = exchange.getTradeById(create_bid_tx.return_value)

    assert exchange.address == first_fake_token.ownerOf(13424)
    assert bid[3] == accounts[3]
    assert bid[6] == False

def test_stake_bidder_nft_from_not_bidder_address_for_bid_and_check(exchange, create_tokens) -> None:
    """ Put bidder NFT from not bidder address for bid and check revert. """
    first_fake_token, second_fake_token = create_tokens
    first_fake_token.mint(13424, accounts[4])

    # Create bid.
    create_bid_tx: TransactionReceipt = exchange.createBid(
        13424,
        25252,
        first_fake_token.address,
        second_fake_token.address,
        700,
        3000,
        {'from': accounts[3]}
    )
    # Stake bidder NFT from another address.
    first_fake_token.approve(exchange.address, 13424, {'from': accounts[4]})
    with reverts("Only a bidder can place a bidder's NFT."):
        exchange.stakeNft(create_bid_tx.return_value, 13424, {'from': accounts[4]})

def test_stake_asker_nft_from_not_asker_address_for_ask_and_check(exchange, create_tokens) -> None:
    """ Put asker NFT from not asker address for ask and check revert. """
    first_fake_token, second_fake_token = create_tokens
    second_fake_token.mint(25252, accounts[4])

    # Create ask.
    create_bid_tx: TransactionReceipt = exchange.createAsk(
        13424,
        25252,
        first_fake_token.address,
        second_fake_token.address,
        4000,
        700,
        {'from': accounts[3]}
    )
    # Stake asker NFT from another address.
    second_fake_token.approve(exchange.address, 25252, {'from': accounts[4]})
    with reverts("Only a asker can place a asker's NFT."):
        exchange.stakeNft(create_bid_tx.return_value, 25252, {'from': accounts[4]})

def test_payment_from_a_bidder_and_check_event(exchange, create_tokens) -> None: 
    # Create bid.
    first_fake_token, second_fake_token = create_tokens

    create_bid_tx: TransactionReceipt = exchange.createBid(
        13424,
        25252,
        first_fake_token.address,
        second_fake_token.address,
        700,
        3000,
        {'from': accounts[3]}
    )
    # Make payment.
    events = exchange.pay(create_bid_tx.return_value, {'from': accounts[3], 'value': 3000}).events
    # Check if the event was called.
    assert events.keys()[0] == 'AmountPaid'
    # Check events items.
    event_items = events['AmountPaid']
    assert 1 == event_items['tradeId']
    assert accounts[3] == event_items['bidder']
    assert 3000 == event_items['amount']

def test_of_payment_for_expired_trade_and_check_revert(exchange, create_tokens) -> None:
    """ Put NFT for expired bid and check revert. """
    first_addr, second_adddr = create_tokens

    # Create bid.
    create_bid_tx: TransactionReceipt = exchange.createBid(
        13424,
        25252,
        first_addr,
        second_adddr,
        700,
        3000,
        {'from': accounts[3]}
    )
    # Time travel. 
    chain.sleep(701)
    with reverts("The timestamp of the trade must be less than the block timestamp value!"):
        exchange.pay(create_bid_tx.return_value, {'from': accounts[3], 'value': 3000})

def test_of_payment_for_bid_with_wrong_amount(exchange, create_tokens) -> None:
    first_addr, second_adddr = create_tokens

    # Create bid.
    create_bid_tx: TransactionReceipt = exchange.createBid(
        13424,
        25252,
        first_addr,
        second_adddr,
        700,
        3000,
        {'from': accounts[3]}
    )
    with reverts("Amount of Wei must be equal to the price!"):
        exchange.pay(create_bid_tx.return_value, {'from': accounts[3], 'value': 2999})

def test_of_payment_for_bid_from_another_address(exchange, create_tokens) -> None:
    first_addr, second_adddr = create_tokens

    # Create bid.
    create_bid_tx: TransactionReceipt = exchange.createBid(
        13424,
        25252,
        first_addr,
        second_adddr,
        700,
        3000,
        {'from': accounts[3]}
    )
    with reverts("The sender's address must match the bidder's address!"):
        exchange.pay(create_bid_tx.return_value, {'from': accounts[4], 'value': 3000})