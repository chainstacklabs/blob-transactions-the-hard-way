import hashlib

# Given KZG commitment
kzg_commitment = "9493a713dd89eb7fe295efd62545bb93bca395a84d18ecfa2c6c650cddc844ad4c1935cbe7d6830967df9d33c5a2e230"

# Remove the '0x' prefix if present
if kzg_commitment.startswith("0x"):
    kzg_commitment = kzg_commitment[2:]

# Convert the KZG commitment to bytes
kzg_commitment_bytes = bytes.fromhex(kzg_commitment)

# Compute the SHA-256 hash of the KZG commitment
sha256_hash = hashlib.sha256(kzg_commitment_bytes).digest()

# Prepend the version byte (0x01) to the last 31 bytes of the SHA-256 hash
version_byte = b'\x01'
blob_versioned_hash = version_byte + sha256_hash[1:]

# Convert to hexadecimal for display
blob_versioned_hash_hex = blob_versioned_hash.hex()

# Print the result
print(f"Blob versioned hash: 0x{blob_versioned_hash_hex}")
