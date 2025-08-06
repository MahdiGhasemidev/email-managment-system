import base64
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


#! Create a key from user password
def generate_key(password: str) -> bytes:
    """Create a safe key name salt """
    #! salt must be random
    salt = b"some_random_salt"
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )
    return kdf.derive(password.encode())

def encrypt(password: str, key: bytes) -> str:
    """Encrypts a password using AES encryption in CBC mode.

    Args:
        password (str): The plaintext password to encrypt.
        key (bytes): The AES encryption key (must be 16, 24, or 32 bytes long).

    Returns:
        str: The base64-encoded string containing the IV and the encrypted password.

    Notes:
        - The password is padded with spaces to ensure its length is a multiple of 16 bytes.
        - A random 16-byte initialization vector (IV) is generated for each encryption.
        - The output is the concatenation of the IV and the encrypted password, encoded in base64.
    """
    """ Use AES to encrypt """
    #! random vicrorization
    iv = os.urandom(16)

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    #! password must be 16 byte
    padded_password = password + (16 - len(password) % 16) * " "  # Padding

    encrypted_password = encryptor.update(padded_password.encode()) + encryptor.finalize()

    #! Return encrypted password base64
    return base64.b64encode(iv + encrypted_password).decode("utf-8")

def decrypt(encrypted_password: str, key: bytes) -> str:
    """Decode using AES"""

    encrypted_password_bytes = base64.b64decode(encrypted_password)

    #! Seperade iv from encrypted
    iv = encrypted_password_bytes[:16]
    encrypted_password_bytes = encrypted_password_bytes[16:]

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    decrypted_password = decryptor.update(encrypted_password_bytes) + decryptor.finalize()

    #! remove space
    return decrypted_password.decode().rstrip()

#  function tests
password = "mysecretpassword"
key = generate_key("securepassword")  #! create a key from function
