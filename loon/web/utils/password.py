from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError


def hash_password(password: str) -> str:
    ph = PasswordHasher()

    hashed = ph.hash(password)

    return str(hashed)


def verify_password(password: str, hashed_password: str) -> bool:
    ph = PasswordHasher()

    try:
        return ph.verify(hashed_password, password)
    except (VerifyMismatchError, InvalidHashError):
        return False
