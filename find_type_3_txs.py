import os
from web3 import Web3
from web3 import Web3, HTTPProvider
from dotenv import load_dotenv

load_dotenv()

w3 = Web3(HTTPProvider(os.getenv("EXECUTION_LAYER_URL")))

# Specify the block number you want to check
block_number = 6090748
block = w3.eth.get_block(block_number, full_transactions=True)

# Iterate through transactions and check for type-3 transactions
for tx in block.transactions:
    if tx.type == 3:  # Type 3 refers to blob transactions
        print("Transaction Hash:", tx.hash.hex())