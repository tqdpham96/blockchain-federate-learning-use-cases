// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract IPFSStorage {
    // --- State ---
    address public owner;

    // maps a key (e.g. workerId) to the IPFS hash URL
    mapping(uint256 => string) private ipfsHashes;

    // who uploaded under this key
    mapping(uint256 => address) public uploader;

    // how much reward (in wei) has been allocated for this key
    mapping(uint256 => uint256) public rewards;

    // whether the uploader already claimed the reward
    mapping(uint256 => bool) public claimed;

    // --- Events ---
    event HashStored(uint256 indexed key, string hash, address indexed uploader);
    event RewardDeposited(uint256 indexed key, uint256 amount);
    event RewardClaimed(uint256 indexed key, address indexed claimer, uint256 amount);

    // --- Modifiers ---
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }

    modifier onlyUploader(uint256 key) {
        require(uploader[key] == msg.sender, "Not uploader");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    // --- IPFS functions ---

    /// @notice Store or update the IPFS hash for a given key.
    /// @param key   A uint identifier (e.g. workerId or iteration).
    /// @param hash  The IPFS URL or content hash string (e.g. https://...).
    function storeHash(uint256 key, string calldata hash) external {
        ipfsHashes[key] = hash;
        uploader[key]    = msg.sender;
        claimed[key]     = false;    // reset any prior claim flag
        emit HashStored(key, hash, msg.sender);
    }

    /// @notice Retrieve the IPFS hash stored under this key.
    function retrieveHash(uint256 key) external view returns (string memory) {
        return ipfsHashes[key];
    }

    // --- Incentive functions ---

    /// @notice Owner can deposit ETH as a reward for a given key.
    /// @param key  The same key used in storeHash.
    function depositReward(uint256 key) external payable onlyOwner {
        require(msg.value > 0, "No ETH sent");
        rewards[key] += msg.value;
        emit RewardDeposited(key, msg.value);
    }

    /// @notice Uploader calls this to claim their deposited reward.
    /// @param key  The key under which they stored their hash.
    function claimReward(uint256 key) external onlyUploader(key) {
        require(!claimed[key], "Already claimed");
        uint256 amount = rewards[key];
        require(amount > 0, "No reward");
        claimed[key] = true;
        // zero out to avoid re‑entrancy
        rewards[key] = 0;
        payable(msg.sender).transfer(amount);
        emit RewardClaimed(key, msg.sender, amount);
    }

    // --- Utility ---

    /// @notice Owner can change the owner address.
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "Invalid address");
        owner = newOwner;
    }

    // Fallback to accept plain ETH transfers (if desired)
    receive() external payable {}
} 