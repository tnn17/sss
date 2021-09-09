// SPDX-License-Identifier: MIT 
pragma solidity 0.8.7;

import "./NFTToNFTExchangeDataEventsAndModifiers.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract NFTToNFTExchange is Ownable, NFTToNFTExchangeDataEventsModifiers {

    constructor(uint _minDuration) public Ownable() {
        minDuration = _minDuration;
    }

    function emitCrateTradeEvent(
        uint _tradeId,
        Trade memory _trade
    ) internal {
        if (_trade.creator == _trade.bidder) {
                emit BidCreated(
                _tradeId,
                _trade.creator,
                _trade.bidder,
                _trade.bidderNFTAddress,
                _trade.askerNFTAddress,
                _trade.bidderNFTId,
                _trade.askerNFTId,
                _trade.price,
                _trade.expirestAt
            );
        } else if (_trade.creator == _trade.asker) {
                emit AskCreated(
                _tradeId,
                _trade.creator,
                _trade.asker,
                _trade.bidderNFTAddress,
                _trade.askerNFTAddress,
                _trade.bidderNFTId,
                _trade.askerNFTId,
                _trade.price,
                _trade.expirestAt
            );
        }
    }

    function determineIfATradeIsPaid(
        uint _tradeId
    ) internal {
        Trade memory trade = idToTrade[_tradeId];
        if (addressToTradeIdToWei[trade.bidder][_tradeId] == trade.price &&
            nftOwnerToTradeIdToNftId[trade.bidder][_tradeId] == trade.bidderNFTId &&
            nftOwnerToTradeIdToNftId[trade.asker][_tradeId] == trade.askerNFTId) {
                idToTrade[_tradeId].paid = true;
            }
        else {
            idToTrade[_tradeId].paid = false;
        }
    }

    function createBid(
        uint _bidderNFTId,
        uint _askerNFTId,
        IERC721 _bidderNFTAddress,
        IERC721 _askerNFTAddress,
        uint _duration,
        uint _price
    ) 
        external 
        payable
        nftNotEqual(
            _bidderNFTId,
            _bidderNFTAddress,
            _askerNFTAddress,
            _askerNFTId
        )
        expirationTimeIsLongerThatMinDuration(
            _duration
            )
        returns(uint) 
    {
        lastTradeId++;

        uint expirestAt = block.timestamp + _duration;
        Trade memory trade = Trade({
            bidder: msg.sender,
            asker: address(0),
            creator: msg.sender,
            bidderNFTAddress: _bidderNFTAddress,
            askerNFTAddress: _askerNFTAddress,
            askerNFTId: _askerNFTId,
            bidderNFTId:_bidderNFTId,
            expirestAt: expirestAt,
            price: _price,
            paid: false,
            bidderReceiveNft: false,
            askerReceiveNft: false,
            askerReceiveWei: false
        });
        idToTrade[lastTradeId] = trade;

        emitCrateTradeEvent(lastTradeId, trade);
        return lastTradeId;
    }

    function createAsk(
        uint _bidderNFTId,
        uint _askerNFTId,
        IERC721 _bidderNFTAddress,
        IERC721 _askerNFTAddress,
        uint _duration,
        uint _price
    )
    external
    nftNotEqual(
            _bidderNFTId,
            _bidderNFTAddress,
            _askerNFTAddress,
            _askerNFTId
        )
    expirationTimeIsLongerThatMinDuration(
        _duration
        )
    returns(uint) {
        lastTradeId++;

        uint expirestAt = block.timestamp + _duration;

        Trade memory trade = Trade({
            bidder: address(0),
            asker: msg.sender,
            creator: msg.sender,
            bidderNFTAddress: _bidderNFTAddress,
            askerNFTAddress: _askerNFTAddress,
            askerNFTId: _askerNFTId,
            bidderNFTId:_bidderNFTId,
            expirestAt: expirestAt,
            price: _price,
            paid: false,
            bidderReceiveNft: false,
            askerReceiveNft: false,
            askerReceiveWei: false
        });
        idToTrade[lastTradeId] = trade;

        emitCrateTradeEvent(lastTradeId, trade);
        return lastTradeId;
    }

    function stakeNft(
        uint _tradeId,
        uint _nftId
    )
    isTradeExist(
        _tradeId
    )
    isTradeAvailable(
        _tradeId
    )
    nftIdIsInTrade(
        _tradeId,
        _nftId
    )
    external {
        Trade storage trade = idToTrade[_tradeId];

        if (_nftId == trade.bidderNFTId) {
            if (trade.bidder == trade.creator) {
                require(msg.sender == trade.bidder,
                "Only a bidder can place a bidder's NFT.");
            }
            trade.bidder = msg.sender;
            // Transfer NFT.
            trade.bidderNFTAddress.safeTransferFrom(
                trade.bidder, address(this), _nftId);
            // Chaning internal storage.
            nftOwnerToTradeIdToNftId[trade.bidder][_tradeId] = _nftId;
        } else if (_nftId == trade.askerNFTId) {
            if (trade.asker == trade.creator) {
                require(msg.sender == trade.asker,
                "Only a asker can place a asker's NFT.");
            }
            trade.asker = msg.sender;
            // Transfer NFT.
            trade.askerNFTAddress.safeTransferFrom(
                trade.asker, address(this), _nftId);
            // Chaning internal storage.
            nftOwnerToTradeIdToNftId[trade.asker][_tradeId] = _nftId;
        }
        determineIfATradeIsPaid(_tradeId);
    }

    function pay(
        uint _tradeId
    ) 
    external
    payable
    isTradeAvailable(
        _tradeId
    )
    isSenderBidder(
        _tradeId
    )
    isTradeExist(
        _tradeId
    )
    weiNotPaidBeforeForThisTrade(
        _tradeId
    )
    {
        require(msg.value == idToTrade[_tradeId].price,
        "Amount of Wei must be equal to the price.");
        addressToTradeIdToWei[msg.sender][_tradeId] += msg.value;
        determineIfATradeIsPaid(_tradeId);
        emit AmountPaid(
            _tradeId,
            msg.sender,
            msg.value
        );
    }
    
    function withdrawNft(
        uint _tradeId
    )
    external
    isTradeAvailable(
        _tradeId
    )
    isTradePaid(
        _tradeId
    )
    {
        Trade memory trade = idToTrade[_tradeId];
        if (msg.sender == trade.bidder) {
            require(nftOwnerToTradeIdToNftId[trade.asker][_tradeId] != 0,
            "NFT is already withdrawed!");
            // Transfer NFT.
            trade.askerNFTAddress.safeTransferFrom(
                address(this), msg.sender, trade.askerNFTId);
            // Chaning internal storage.
            nftOwnerToTradeIdToNftId[trade.asker][_tradeId] = 0;
            trade.bidderReceiveNft = true;
            emit NftWithdrawed(
                _tradeId, msg.sender, trade.askerNFTId);
        } else if (msg.sender == trade.asker) {
            require(nftOwnerToTradeIdToNftId[trade.bidder][_tradeId] != 0,
            "NFT is already withdrawed!");
            // Transfer NFT.
            trade.bidderNFTAddress.safeTransferFrom(
                address(this), msg.sender, trade.bidderNFTId);
            // Chaning internal storage.
            nftOwnerToTradeIdToNftId[trade.bidder][_tradeId] = 0;
            trade.askerReceiveNft = true;
            emit NftWithdrawed(
                _tradeId, msg.sender, trade.bidderNFTId);
        } 
    }

    function withdrawWei(
        uint _tradeId
    )
    external
    isTradeAvailable(
        _tradeId
    )
    isTradePaid(
        _tradeId
    ) 
    isSenderAsker(
        _tradeId
    )
    {   
        Trade memory trade = idToTrade[_tradeId];
        require(addressToTradeIdToWei[trade.bidder][_tradeId] != 0,
        "Wei is already withdrawed.");
        payable(msg.sender).transfer(trade.price);
        addressToTradeIdToWei[trade.bidder][_tradeId] = 0;
        trade.askerReceiveWei = true;
        emit WeiWithdrawed(_tradeId, msg.sender, trade.price);
    }

    function unstakeNft(
        uint _tradeId
    )
    external {
        Trade memory trade = idToTrade[_tradeId];
        if (
            trade.bidderReceiveNft == false &&
            trade.askerReceiveNft == false &&
            trade.askerReceiveWei == false 
        ) {
            if (trade.bidder == msg.sender &&
            nftOwnerToTradeIdToNftId[msg.sender][_tradeId] == trade.bidderNFTId) {
                trade.bidderNFTAddress.safeTransferFrom(
                    address(this), msg.sender, trade.bidderNFTId);
                nftOwnerToTradeIdToNftId[msg.sender][_tradeId] = 0;
            } else if (trade.asker == msg.sender &&
            nftOwnerToTradeIdToNftId[msg.sender][_tradeId] == trade.askerNFTId) {
                trade.askerNFTAddress.safeTransferFrom(
                    address(this), msg.sender, trade.askerNFTId);
                nftOwnerToTradeIdToNftId[msg.sender][_tradeId] = 0;
            }
        }
    }

    function unstakeWei(
        uint _tradeId
    )
    external
    isSenderBidder(
        _tradeId
    ) {
        Trade memory trade = idToTrade[_tradeId];
        if (
            trade.bidderReceiveNft == false &&
            trade.askerReceiveWei == false &&
            trade.askerReceiveWei == false
        ) {
            if (addressToTradeIdToWei[trade.asker][_tradeId] == trade.price) {
                payable(trade.asker).transfer(trade.price);
                addressToTradeIdToWei[trade.asker][_tradeId] = 0;
            }
        }
    }
   
    function getTradeById(
        uint _tradeId
    )
    external 
    view
    isTradeExist(
        _tradeId
    )
    returns (uint, IERC721, IERC721, address, address, address, bool, uint256, uint256, uint256) {
        Trade memory trade = idToTrade[_tradeId];

        return (
            _tradeId,
            trade.bidderNFTAddress,
            trade.askerNFTAddress,
            trade.bidder,
            trade.asker,
            trade.creator,
            trade.paid,
            trade.bidderNFTId,
            trade.askerNFTId,
            trade.price
        );
    }
}
