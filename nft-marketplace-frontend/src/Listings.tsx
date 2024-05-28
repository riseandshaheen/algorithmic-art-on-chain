import { ethers } from "ethers";
import { useEffect } from "react";
import * as abi from "./Listings.json"

interface IListingPropos {
    dappAddress: string 
}

export const Listings: React.FC<IListingPropos> = (propos) => {
    const NFTEXCHANGE_ADDRESS = "0x948B3c65b89DF0B4894ABE91E6D02FE579834F8F"
    const abi = [
        "event ListingCreated(uint256 indexed id, address indexed nftContract, uint256 indexed tokenId, address seller, uint256 price)"
    ];
    console.log("ABI: ", abi)
    const provider = new ethers.providers.JsonRpcProvider("http://localhost:8545")
    const exchangeContract = new ethers.Contract(NFTEXCHANGE_ADDRESS, abi, provider)
    
    const handleListing = ( id: ethers.BigNumber, nftContract: string, tokenId: ethers.BigNumber, seller: string, price: ethers.BigNumber ) => {
        console.log("ListingCreated Event:");
        console.log("ID:", id.toString());
        console.log("NFT Contract:", nftContract);
        console.log("Token ID:", tokenId.toString());
        console.log("Seller:", seller);
        console.log("Price:", ethers.utils.formatEther(price));

    }

    useEffect( () => {
        exchangeContract.on("ListingCreated", handleListing)
        return () => {
            exchangeContract.removeAllListeners("ListingCreated");
        }
    }, [])
     return(
        <div><p>Hello</p></div>
    );
}