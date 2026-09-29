import os
from dotenv import load_dotenv
from jose import jwt
from datetime import datetime, timedelta, timezone
import bcrypt
from cryptography.fernet import Fernet

load_dotenv()

VAULT_ENCRYPTION_KEY = os.getenv("VAULT_ENCRYPTION_KEY")


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password.decode("utf-8")

SECRET_KEY = "change-this-later"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )
def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload
    except Exception:
        return None
    
def encrypt_password(password: str) -> str:
    fernet = Fernet(VAULT_ENCRYPTION_KEY.encode())
    encrypted_password = fernet.encrypt(password.encode("utf-8"))
    return encrypted_password.decode("utf-8")

def decrypt_password(encrypted_password: str) -> str:
    fernet = Fernet(VAULT_ENCRYPTION_KEY.encode())
    decrypted_password = fernet.decrypt(
        encrypted_password.encode("utf-8")
    )
    return decrypted_password.decode("utf-8")