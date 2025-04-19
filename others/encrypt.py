from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

# --- Generate RSA Keys ---
def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    return private_key, public_key

# --- Encrypt a message ---
def encrypt_message(public_key, message: str) -> bytes:
    ciphertext = public_key.encrypt(
        message.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext

# --- Decrypt a message ---
def decrypt_message(private_key, ciphertext: bytes) -> str:
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return plaintext.decode()

# --- Example usage ---
if __name__ == "__main__":
    private_key, public_key = generate_keys()

    message = "Hello, RSA encryption!"
    print(f"Original message: {message}")

    encrypted = encrypt_message(public_key, message)
    print(f"Encrypted message (bytes): {encrypted}")

    decrypted = decrypt_message(private_key, encrypted)
    print(f"Decrypted message: {decrypted}")
