import jwt
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
    BaseUser,
    requires as _requires,
)
from starlette.requests import HTTPConnection
from starlette.responses import JSONResponse, Response
from sqlmodel import Session, select

from loon.web.db import engine
from loon.web.users.models import User
from loon.web.utils.jwt import JWT_SECRET, JWT_ALGORITHM

authenticated = _requires("authenticated", status_code=401)
admin = _requires(["authenticated", "admin"], status_code=403)


class AuthenticatedUser(BaseUser):
    def __init__(self, user: User) -> None:
        self.user = user

    @property
    def is_authenticated(self) -> bool:
        return True

class JWTAuthBackend(AuthenticationBackend):
    def _extract_token(self, conn: HTTPConnection) -> str | None:
        auth_header = conn.headers.get("Authorization")
        if auth_header is not None:
            scheme, _, credentials = auth_header.partition(" ")
            if scheme.lower() == "bearer" and credentials:
                return credentials

        # Browser WebSocket APIs cannot set Authorization headers.
        token = conn.query_params.get("token")
        return token or None

    async def authenticate(
        self, conn: HTTPConnection
    ) -> tuple[AuthCredentials, AuthenticatedUser] | None:
        credentials = self._extract_token(conn)
        if credentials is None:
            return None

        try:
            payload = jwt.decode(credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid or expired token")

        user_id = payload.get("user_id")
        if not isinstance(user_id, int):
            raise AuthenticationError("Invalid or expired token")

        with Session(engine) as session:
            user = session.exec(select(User).where(User.id == user_id)).first()

        if user is None:
            raise AuthenticationError("User not found")

        scopes = ["authenticated"]

        if user.admin:
            scopes.append("admin")

        return AuthCredentials(scopes), AuthenticatedUser(user)


def on_auth_error(conn: HTTPConnection, exc: Exception) -> Response:
    return JSONResponse({"detail": str(exc)}, status_code=401)
