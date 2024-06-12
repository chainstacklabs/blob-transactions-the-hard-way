import ckzg

def bytes_from_hex(hexstring):
    return bytes.fromhex(hexstring.replace("0x", ""))

if __name__ == "__main__":
    ts = ckzg.load_trusted_setup("trusted_setup.txt")
    
    with open("blob.txt", "r") as file:
        blob_hex = file.read().strip()
        blob = bytes_from_hex(blob_hex)
    
    # Compute KZG commitment
    commitment = ckzg.blob_to_kzg_commitment(blob, ts)
    
    # Print the commitment in hexadecimal format
    print("KZG Commitment:", commitment.hex())
