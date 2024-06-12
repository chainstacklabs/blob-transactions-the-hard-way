import os
import requests
from web3 import Web3, HTTPProvider
from dotenv import load_dotenv
import ckzg
import hashlib

load_dotenv()

# Connect to the Ethereum Execution Layer
w3 = Web3(HTTPProvider(os.getenv("EXECUTION_LAYER_URL")))

# Specify the block number you want to check
block_number = 6090748
block = w3.eth.get_block(block_number, full_transactions=True)

# Find type-3 transactions
type_3_tx_hashes = [tx.hash.hex() for tx in block.transactions if tx.type == 3]

# Store blob versioned hashes in a dictionary
blob_versioned_hashes_dict = {}
for tx_hash in type_3_tx_hashes:
    tx_details = w3.eth.get_transaction(tx_hash)
    blob_versioned_hashes = tx_details.get('blobVersionedHashes', [])
    if blob_versioned_hashes:
        blob_versioned_hashes_dict[tx_hash] = blob_versioned_hashes[0].hex()

# Extract the parentBeaconBlockRoot from the block data
parent_beacon_block_root = block['parentBeaconBlockRoot']

# Convert byte string to hexadecimal string
parent_beacon_block_root_hex = parent_beacon_block_root.hex()

# Ensure it starts with '0x'
if not parent_beacon_block_root_hex.startswith('0x'):
    parent_beacon_block_root_hex = '0x' + parent_beacon_block_root_hex

# Print the parentBeaconBlockRoot for visibility
print("parentBeaconBlockRoot being queried:", parent_beacon_block_root_hex)

# Use parentBeaconBlockRoot for further queries
headers_url = f"{os.getenv('CONSENSUS_LAYER_URL')}/eth/v1/beacon/headers/{parent_beacon_block_root_hex}"

header_response = requests.get(headers_url)
if header_response.status_code != 200:
    print("Failed to fetch data:", header_response.status_code)
    print(header_response.text)
    exit()

header_data = header_response.json()
if 'data' not in header_data:
    print("Unexpected response format:", header_data)
    exit()

slot_number = int(header_data['data']['header']['message']['slot']) + 1

# Retrieve blobs
blobs_url = f"{os.getenv('CONSENSUS_LAYER_URL')}/eth/v1/beacon/blob_sidecars/{slot_number}"
blobs_response = requests.get(blobs_url).json()
blobs = blobs_response['data']

# Process each blob
results = []
for i, tx_hash in enumerate(type_3_tx_hashes):
    blob = blobs[i]
    print(f"Retrieved KZG commitment for transaction {tx_hash}: {blob['kzg_commitment']}")
    
    blob_data_hex = blob['blob']
    
    # Save blob data to a file
    with open(f"blob{i}.txt", "w") as file:
        file.write(blob_data_hex)

    # Load blob data from the file and ensure it's correct
    with open(f"blob{i}.txt", "r") as file:
        blob_hex = file.read().strip()
        blob_data = bytes.fromhex(blob_hex.replace("0x", ""))  # Ensure consistent handling
        print(f"Blob data file for transaction {tx_hash}: blob{i}.txt")

    # Load trusted setup
    ts = ckzg.load_trusted_setup("trusted_setup.txt")

    # Compute KZG commitment
    commitment = ckzg.blob_to_kzg_commitment(blob_data, ts)
    print(f"Locally computed KZG commitment for transaction {tx_hash}: {commitment.hex()}")
    
    # Compute versioned hash
    sha256_hash = hashlib.sha256(commitment).digest()
    versioned_hash = b'\x01' + sha256_hash[1:]
    
    # Compare with network data, ignoring the '0x' prefix
    network_commitment = blob['kzg_commitment']
    local_commitment_hex = '0x' + commitment.hex()

    commitment_match = local_commitment_hex == network_commitment
    print(f"KZG commitment match for transaction {tx_hash}: {commitment_match}")
    
    # Use the stored blob versioned hashes during blob processing
    network_versioned_hash = blob_versioned_hashes_dict.get(tx_hash, "No blob versioned hash found")
    print(f"Network versioned hash for transaction {tx_hash}: {network_versioned_hash}")
    
    print(f"Blob data file for transaction {tx_hash}: blob{i}.txt")
    print(f"Locally computed KZG commitment for transaction {tx_hash}: {commitment.hex()}")
    print(f"Locally computed versioned hash for transaction {tx_hash}: {versioned_hash.hex()}")
    print()
    
    results.append({
        'transaction_hash': tx_hash,
        'commitment': commitment.hex(),
        'versioned_hash': versioned_hash.hex(),
        'commitment_match': commitment_match,
        'versioned_hash_match': versioned_hash.hex() == network_versioned_hash
    })

print("### SUMMARY ###")
print(f"Block {block_number}, Slot {slot_number}")
print("Type-3 transactions:", type_3_tx_hashes)
print()
for result in results:
    print(f"TX:{result['transaction_hash']}:")
    print(f"KZG: {result['commitment']}")
    print(f"Versioned hash: {result['versioned_hash']}")
    print(f"Locally computed match for the retrieved blob:")
    print(f"KZG commitment: {result['commitment_match']}")
    print(f"Versioned hash: {result['versioned_hash_match']}")
    print()