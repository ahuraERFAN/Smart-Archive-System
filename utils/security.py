import hashlib
import os


def hash_password(password: str) -> str:

    salt = os.urandom(32)
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000
    )
    return salt.hex() + pwd_hash.hex()


def verify_password(password: str, stored_hash: str) -> bool:

    salt = bytes.fromhex(stored_hash[:64])
    stored_pwd_hash = stored_hash[64:]

    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000
    ).hex()

    return pwd_hash == stored_pwd_hash
