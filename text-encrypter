from cryptography.fernet import Fernet

# Generate a new key (only once). Save this key if you want to reuse it.
key = Fernet.generate_key()
cipher = Fernet(key)

def encrypt_message(message: str) -> bytes:
    """Encrypt text and return the encrypted token."""
    return cipher.encrypt(message.encode())

def decrypt_message(token: bytes) -> str:
    """Decrypt token back into text."""
    return cipher.decrypt(token).decode()

if __name__ == "__main__":
    text = input("Enter text to encrypt: ")
    encrypted = encrypt_message(text)
    print("\n🔒 Encrypted:", encrypted)

    decrypted = decrypt_message(encrypted)
    print("🔓 Decrypted:", decrypted)
