import os
from eth_abi import abi
from eth_account import Account
from eth_utils import to_hex
from web3 import Web3, HTTPProvider
from dotenv import load_dotenv

load_dotenv()

w3 = Web3(HTTPProvider(os.getenv("EXECUTION_LAYER_URL")))

"""
Add the web3py middleware to ensure compatibility with Erigon 2
as the eth_estimateGas only expects one argument. The block number or
block hash was dropped in https://github.com/ledgerwatch/erigon/releases/tag/v2.60.1
"""
def erigon_compatibility_middleware(make_request, w3):
    def middleware(method, params):
        if method == 'eth_estimateGas' and len(params) > 1:
            # Modify the params to include only the transaction object
            params = params[:1]
        return make_request(method, params)
    return middleware
w3.middleware_onion.add(erigon_compatibility_middleware)

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
    "chainId": 11155111,  # Sepolia 11155111; Holesky 17000
    "from": acct.address,
    "to": "0x0000000000000000000000000000000000000000", # Does not matter what account you send it to
    "value": 0,
    "maxFeePerGas": 10**12,
    "maxPriorityFeePerGas": 10**12,
    "maxFeePerBlobGas": to_hex(10**12), # Note the new type-3 parameter for blobs
    "nonce": w3.eth.get_transaction_count(acct.address),
}

# Now you can estimate gas as usual
gas_estimate = w3.eth.estimate_gas(tx)
tx["gas"] = gas_estimate

# Proceed with the rest of your script
signed = acct.sign_transaction(tx, blobs=[BLOB_DATA])
tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"TX receipt: {tx_receipt}")
