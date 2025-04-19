<a id="readme-top"></a>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

This project leverages FL to enable localized model training across multiple sites while utilizing BC to ensure trust, transparency, and data integrity accross the network. The details paper can be seen at: https://arxiv.org/pdf/2503.05725

It addresses key challenges as:
* Maintaining privacy and security
* Ensuring transparency and fairness
* Incentivizing participation in decentralized networks

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

This porject uses the following programming languages:

* Python (for main code)
* Solidity (for smart contract)
* Binance Smart Chain (for deploying smart contract)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

Follow the below guidelines to start

### Prerequisites

* Python
* Solidity
* NFT.Storage API Key (nft.storage)
* Binance Smart Chain test net API Key and RPC URL
* Hardhat

### Installation

1. Get an API Key at [https://nft.storage/](https://nft.storage/)
2. Get the API Key and RPC URL at: [http://testnet.bscscan.com/](http://testnet.bscscan.com/)
3. Get the Wallet Private key and insert in smart_contract/hardhat.config.js
4. Clone the repo
   ```sh
   git clone https://github.com/tqdpham96/blockchain-federate-learning-use-cases
   ```
5. Install python and solidity packages
   * Python
   ```sh
   pip instal requirements.txt
   ```

   * Solidity
   ```sh
   cd smart_contract
   npm install
   ```
6. Deploy Smart contract to BSC testnet

   ```sh
   npx hardhat deploy --network bsc-testnet
   npx hardhat verify --network bsc-testnet 0xYourContractAddress
   ```

7. Enter your API in `main.py` and ipfs_upload.py

  ```sh
  NFT_STORAGE_API_KEY = 'your_nft_storage_api_key_here' 
  contract_address = "0xYourDeployedContractAddress"
  w3 = Web3(Web3.HTTPProvider("RPC_URL"))
  ```
8. Download the NASA's CMAPSS datasetdataset

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

After finish setting up the repo as well as the API Key. The following example can be run:

* main.py: Performing the FL study in the context of RUL predictions for components or systems by 10 workers. 
As soon as the worker finish training, the weights will be uploaded to blockchain for transparency. Then, a read function within the blockchain smart contract is invovked to
access the recorded hash.
* smart_contract: Function to upload ipfh hash without and with incentive in terms of native token, i.e., BNB in BSC or ETH in Ethereum.
* ipfs_upload.py: Function to transform data to ipfs hash
* others/encrypt.py: Perform RSA encrypt/decrypt algorithmalgorithm


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [x] Add Changelog
- [x] Add back to top links
- [ ] Add Additional Templates w/ Examples
- [ ] Add "components" document to easily copy & paste sections of the readme
- [ ] Add Smart Contract for training the ML directly in blockchain
- [ ] UI/Software

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<!-- LICENSE -->
## License

Distributed under the Unlicense License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>