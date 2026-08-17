import time
from typing import Literal

import jwt

from config import settings

JWT_SECRET = settings.jwt.secret
JWT_ALGORITHM = "HS256"


def _encode_jwt(user_id: int, ttl: int, typ: Literal["ws", "web"]) -> str:
    payload = {
        "user_id": user_id,
        "exp": int(time.time()) + ttl,
        "typ": typ,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def generate_token(user_id: int) -> str:
    return _encode_jwt(user_id, settings.jwt.access_ttl, "web")


def generate_ws_token(user_id: int) -> str:
    return _encode_jwt(user_id, settings.jwt.ws_ttl, "ws")


def decode_token(token: str) -> dict:
    payload = jwt.decode(token, JWT_SECRET)
    return payload
