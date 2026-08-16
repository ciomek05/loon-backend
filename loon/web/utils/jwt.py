import time

import jwt

from config import settings

JWT_SECRET = settings.jwt.secret
JWT_ALGORITHM = "HS256"


def generate_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "exp": int(time.time()) + 60 * 60 * 24,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    payload = jwt.decode(token, JWT_SECRET)
    return payload