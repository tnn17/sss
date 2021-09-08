// SPDX-License-Identifier: MIT 
pragma solidity 0.8.7;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";

contract NFTToNFTExchangeDataEventsModifiers {
    address internal zero;
    uint internal minDuration;
    uint internal lastTradeId;
    mapping (address => mapping(uint => uint)) 
    internal nftOwnerToTradeIdToNftId;
    mapping (uint => Trade) internal idToTrade;
    mapping (address => mapping(uint => uint)) 
    internal addressToTradeIdToWei;
    mapping (IERC721 => uint) internal NFTThatAlreadyStaked;

    struct Trade {
        address bidder;
        address asker;
        address creator;
        IERC721 bidderNFTAddress;
        IERC721 askerNFTAddress;
        uint askerNFTId;
        uint bidderNFTId;
        uint expirestAt;
        uint price;
        bool paid;
        bool bidderReceiveNft;
        bool askerReceiveNft;
        bool askerReceiveWei;
    }

    modifier nftNotEqual(
        uint _bidderNFTId,
        IERC721 _bidderNFTAddress,
        IERC721 _askerNFTAddress,
        uint _askerNFTId
    ) {
        if (_bidderNFTAddress == _askerNFTAddress) {
            require(_bidderNFTId != _askerNFTId, "NFT cannot be the same!");
        }
        _;
    }

    modifier expirationTimeIsLongerThatMinDuration(
        uint _duration
    ) {
        require(_duration >= minDuration, 
        "The duration value cannot be less than the minimum duration value!");
        _;
    }

    modifier senderIsAskerOrBidder(
        uint _tradeId
    ) {
        require((msg.sender == idToTrade[_tradeId].bidder) || 
        (msg.sender == idToTrade[_tradeId].asker),
        "msg.sender must bu asker or bidder!");
        _;
    }

    modifier nftIdIsInTrade(
        uint _tradeId,
        uint _nftId
    ) {
        require((_nftId == idToTrade[_tradeId].bidderNFTId) &&
        (_nftId == idToTrade[_tradeId].askerNFTId),
        "The NFT identifier is not the seller's NFT or the buyer's NFT!");
        _;
    }

    modifier isTradeExist(
        uint _tradeId
    ) {
        require(idToTrade[_tradeId].expirestAt != 0,
        "Trade does not exist!");
        _;
    }

    modifier isTradePaid(
        uint _tradeId
    ) {
        Trade memory trade = idToTrade[_tradeId];
        require(trade.paid, "Trade must be paid!!");
        _;
    }

    modifier isSenderBidder(
        uint _tradeId
    ) {
        require(idToTrade[_tradeId].bidder == msg.sender,
        "The sender's address must match the bidder's address!");
        _;
    }

    modifier isSenderAsker(
        uint _tradeId
    ) {
        require(idToTrade[_tradeId].asker == msg.sender,
        "The sender's address must match the asker's address!");
        _;
    }

    modifier isTradeAvailable(
        uint _tradeId
    ) {
        require(idToTrade[_tradeId].expirestAt > block.timestamp,
        "The timestamp of the trade must be less than the block timestamp value!");
        _;
    }

    modifier NFTNotPaidBefore(
        uint _nftId,
        uint _tradeId
    ) {
        Trade memory trade = idToTrade[_tradeId];
        if (trade.bidderNFTId == _nftId) {
            require(NFTThatAlreadyStaked[trade.bidderNFTAddress] == 0);
        }
        else if (trade.askerNFTId == _nftId) {
            require(NFTThatAlreadyStaked[trade.askerNFTAddress] == 0);
        }
        _;
    }

    modifier weiNotPaidBeforeForThisTrade(
        uint _tradeId
    ) {
        require(addressToTradeIdToWei[msg.sender][_tradeId] == 0);
        _;
    }

    event BidCreated(
        uint indexed TradeId,
        address creator,
        address bidderAddress,
        IERC721 bidderNFTAddress,
        IERC721 askerNFTAddress,
        uint indexed bidderNFTId,
        uint indexed askerNFTId,
        uint price,
        uint expirestAt
    );

    event AskCreated(
        uint indexed TradeId,
        address creator,
        address askerAddress,
        IERC721 bidderNFTAddress,
        IERC721 askerNFTAddress,
        uint indexed bidderNFTId,
        uint indexed askerNFTId,
        uint price,
        uint expirestAt
    );

    event NftStaked(
        uint indexed tradeId,
        IERC721 indexed nftAddress,
        uint indexed nftId
    );

    event AmountPaid(
        uint indexed tradeId,
        address indexed bidder,
        uint indexed amount
    );

    event NftWithdrawed(
        uint indexed tradeId,
        address indexed to,
        uint indexed nftId
    );

    event WeiWithdrawed(
        uint indexed tradeId,
        address indexed to,
        uint indexed amount
    );

}