import { ethers } from "ethers";
import { useEffect, useState } from "react";
//import exchangeABI from "./Listings.json"
const contractabi = require("./Listings.json")

interface IListingPropos {
    dappAddress: string 
}

interface Listing {
    id: string;
    nftContract: string;
    tokenId: string;
    seller: string;
    price: string;
}

export const Listings: React.FC<IListingPropos> = (propos) => {
    const NFTEXCHANGE_ADDRESS = "0x4ed7c70F96B99c776995fB64377f0d4aB3B0e1C1"
    console.log("marketplace ABI: ", contractabi)
    const provider = new ethers.providers.JsonRpcProvider("http://localhost:8545")
    const exchangeContract = new ethers.Contract(NFTEXCHANGE_ADDRESS, contractabi, provider)

    const [listings, setListings] = useState<Listing[]>([]);
    
    const handleListing = ( id: ethers.BigNumber, nftContract: string, tokenId: ethers.BigNumber, seller: string, price: ethers.BigNumber ) => {
        console.log("ListingCreated Event:");
        console.log("ID:", id.toString());
        console.log("NFT Contract:", nftContract);
        console.log("Token ID:", tokenId.toString());
        console.log("Seller:", seller);
        console.log("Price:", ethers.utils.formatEther(price));

        const newListing: Listing = {
            id: id.toString(),
            nftContract,
            tokenId: tokenId.toString(),
            seller,
            price: ethers.utils.formatEther(price)
        };
        setListings((prevListings) => [...prevListings, newListing]);
    }

    useEffect( () => {
        exchangeContract.on("ListingCreated", handleListing)
        return () => {
            exchangeContract.removeAllListeners("ListingCreated");
        }
    }, [])
     return(
        <div><p>All Listings</p>
        <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>NFT Contract</th>
                        <th>Token ID</th>
                        <th>Seller</th>
                        <th>Price</th>
                    </tr>
                </thead>
                <tbody>
                    {listings.map((listing, index) => (
                        <tr key={index}>
                            <td>{listing.id}</td>
                            <td>{listing.nftContract}</td>
                            <td>{listing.tokenId}</td>
                            <td>{listing.seller}</td>
                            <td>{listing.price} ETH</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}