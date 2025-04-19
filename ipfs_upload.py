import json
from web3 import Web3
import requests
import numpy as np

# ====== CONFIGURATION ======
NFT_STORAGE_API_KEY = 'your_nft_storage_api_key_here'  # <-- Put your API key here
contract_address = "0xYourDeployedContractAddress"
w3 = Web3(Web3.HTTPProvider("RPC_URL"))

# ====== Upload to NFT.storage without saving file ======
def upload_json_to_nft_storage(data_dict, api_key):
    url = "https://api.nft.storage/upload"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    # Convert the Python dict directly to JSON bytes
    files = {
        "file": ("data.json", data_dict, "application/json")
    }
    response = requests.post(url, headers=headers, files=files)

    if response.status_code == 200:
        cid = response.json()["value"]["cid"]
        return f"https://{cid}.ipfs.nftstorage.link/"
    else:
        raise Exception(f"Failed to upload: {response.text}")



# replace with your deployed contract info

contract_abi     = json.load(open('IPFSStorage.abi'))

# load contract
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# unlock / load your account
acct = w3.eth.account.from_key("0xYOUR_PRIVATE_KEY")
w3.eth.default_account = acct.address

def publish_weights_to_ipfs_and_chain(weights: np.ndarray, key: int):
    # 1) dump weights to JSON (or bytes)
    res = json.dumps(weights).encode('utf-8')

    # 2) upload to IPFS
    ipfs_hash = upload_json_to_nft_storage(res, key)  # for add_bytes, `res` is the hash (e.g. "Qm…")

    print(f"  → IPFS hash: {ipfs_hash}")

    # 3) build & send transaction to store in smart contract
    tx = contract.functions.storeHash(key, ipfs_hash).buildTransaction({
        "from": acct.address,
        "nonce": w3.eth.getTransactionCount(acct.address),
        "gas": 200_000,
        "gasPrice": w3.toWei("20", "gwei")
    })
    signed = acct.sign_transaction(tx)
    tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    print(f"  → Stored on‑chain in tx {receipt.transactionHash.hex()} at key={key}")

    return ipfs_hash, receipt

def retrieve_weights_from_chain(key: int) -> np.ndarray:
    """
    1) Calls the smart‐contract retrieveHash(key) → gateway URL.
    2) HTTP‐GETs that URL → JSON with {"w": [...]}.
    3) Returns np.ndarray((d,1)).
    """
    # on‐chain lookup
    url = contract.functions.retrieveHash(key).call()
    print(f" → fetched URL from chain: {url}")

    # HTTP GET JSON
    resp = requests.get(url)
    resp.raise_for_status()
    payload = resp.json()
    w_list  = payload["w"]
    w_arr   = np.array(w_list, dtype=np.float32).reshape(-1,1)
    return w_arr
