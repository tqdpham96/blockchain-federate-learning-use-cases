const hre = require("hardhat");

async function main() {
    // We get the contract to deploy
    const contract = await hre.ethers.getContractFactory("IPFSStorage");
    const final = await contract.deploy();
    await final.deployed();

    console.log("Contract deployed to:", final.address);
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });