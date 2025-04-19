require("@nomiclabs/hardhat-waffle");
require("@openzeppelin/hardhat-upgrades");
require("@nomiclabs/hardhat-ethers");
require("@nomiclabs/hardhat-etherscan");
require("dotenv").config();


module.exports = {
    solidity: {
        compilers: [
            {
                version: "0.8.4",
                settings: {
                    optimizer: {
                        enabled: true,
                        runs: 200,
                    },
                },
            },
        ],
    },
    networks: {
        hardhat: {},
        ropsten: {
            accounts: [""],
            chainId: 3,
            url: "",
            gas: 4100000,
            gasPrice: 50000000000
        },
        "bsc-testnet": {
            accounts: [""],
            chainId: 97,
            url: "https://data-seed-prebsc-1-s1.binance.org:8545/",
            gas: 2100000,
            gasPrice: 10000000000
        },
        "bsc-mainnet": {
            accounts: [""],
            chainId: 56,
            url: "https://bsc-dataseed1.ninicoin.io/",
            gas: 2100000,
            gasPrice: 10000000000
        },
    },
    etherscan: {
        apiKey: '', //bsc
    },
};