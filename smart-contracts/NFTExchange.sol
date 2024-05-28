// Copyright 2021 Cartesi Pte. Ltd.

// SPDX-License-Identifier: Apache-2.0
// Licensed under the Apache License, Version 2.0 (the "License"); you may not use
// this file except in compliance with the License. You may obtain a copy of the
// License at http://www.apache.org/licenses/LICENSE-2.0

// Unless required by applicable law or agreed to in writing, software distributed
// under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
// CONDITIONS OF ANY KIND, either express or implied. See the License for the
// specific language governing permissions and limitations under the License.
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract NFTExchange is Ownable {
    using Counters for Counters.Counter;
    Counters.Counter private _listingIds;

    struct Listing {
        uint256 id;
        address nftContract;
        uint256 tokenId;
        address payable seller;
        uint256 price;
        bool isSold;
    }

    mapping(uint256 => Listing) public listings;

    event ListingCreated(uint256 indexed id, address indexed nftContract, uint256 indexed tokenId, address seller, uint256 price);
    event ListingSold(uint256 indexed id, address indexed buyer);

    constructor() Ownable(msg.sender) {}

    function createListing(address nftContract, uint256 tokenId, uint256 price) public {

        // Check if the contract is approved to transfer the NFT
        require(
            IERC721(nftContract).getApproved(tokenId) == address(this) ||
            IERC721(nftContract).isApprovedForAll(msg.sender, address(this)),
            "Contract is not approved to transfer this NFT"
        );

        IERC721(nftContract).transferFrom(msg.sender, address(this), tokenId);
	    
	    _listingIds.increment();
	    uint256 listingId = _listingIds.current();

	    listings[listingId] = Listing({
            id: listingId,
            nftContract: nftContract,
            tokenId: tokenId,
            seller: payable(msg.sender),
            price: price,
            isSold: false
	    });

	    emit ListingCreated(listingId, nftContract, tokenId, msg.sender, price);
	}

    function buyNFT(uint256 listingId) public payable {
        Listing storage listing = listings[listingId];
        require(!listing.isSold, "NFT is already sold");
        require(msg.value >= listing.price, "Insufficient funds");

        listing.seller.transfer(listing.price);
        IERC721(listing.nftContract).transferFrom(address(this), msg.sender, listing.tokenId);

        listing.isSold = true;

        emit ListingSold(listingId, msg.sender);
    }
}
