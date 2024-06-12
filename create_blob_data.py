import os
from eth_abi import abi

def create_blob_data(text):
    # Encode the text using Ethereum ABI encoding for a string
    encoded_text = abi.encode(["string"], [text])
    
    # Calculate the required padding to make the blob size exactly 131072 bytes or 128 KB
    required_padding = 131072 - (len(encoded_text) % 131072)
    
    # Create the BLOB_DATA with the correct padding
    BLOB_DATA = (b"\x00" * required_padding) + encoded_text
    
    return BLOB_DATA

def main():
    text = "Chainstack" # If you change this, make sure you update the padding
    
    # Create blob data
    blob_data = create_blob_data(text)
    
    # Print the blob data in hexadecimal format
    print(blob_data.hex())

if __name__ == "__main__":
    main()