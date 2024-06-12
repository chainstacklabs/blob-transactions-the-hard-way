import os
from eth_abi import abi
from eth_account import Account
from eth_utils import to_hex
from web3 import Web3, HTTPProvider
from dotenv import load_dotenv

load_dotenv()

w3 = Web3(HTTPProvider(os.getenv("EXECUTION_LAYER_URL")))

text = "Chainstack"
encoded_text = abi.encode(["string"], [text])

# Calculate the required padding to make the blob size exactly 131072 bytes
required_padding = 131072 - (len(encoded_text) % 131072)

# Create the BLOB_DATA with the correct padding
BLOB_DATA = (b"\x00" * required_padding) + encoded_text

pkey = os.environ.get("PRIVATE_KEY")
acct = w3.eth.account.from_key(pkey)

tx = {
    "type": 3, # Type-3 transaction
    "chainId": 11155111,  # Sepolia
    "from": acct.address,
    "to": "0x0000000000000000000000000000000000000000", # Does not matter what account you send it to
    "value": 0,
    "maxFeePerGas": 10**12,
    "maxPriorityFeePerGas": 10**12,
    "maxFeePerBlobGas": to_hex(10**12), # Note the new type-3 parameter for blobs
    "nonce": w3.eth.get_transaction_count(acct.address),
}

gas_estimate = w3.eth.estimate_gas(tx)
tx["gas"] = gas_estimate

signed = acct.sign_transaction(tx, blobs=[BLOB_DATA])
tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"TX receipt: {tx_receipt}")
