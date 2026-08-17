from fastapi import APIRouter, HTTPException, Request, status
from sqlmodel import Session, select

from loon.web import limiter
from loon.web.auth.middleware import authenticated
from loon.web.auth.schema import JWTResponse, JWTRequest
from loon.web.db import engine
from loon.web.users.models import User
from loon.web.utils.jwt import generate_token, generate_ws_token
from loon.web.utils.password import verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/jwt/", response_model=JWTResponse)
@limiter.limit("5/minute")
async def get_jwt(request: Request, body: JWTRequest) -> JWTResponse:
    with Session(engine) as session:
        statement = select(User).where(User.internal_username == body.username)
        user = session.exec(statement).first()

        if user is None or user.id is None or not verify_password(body.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        return JWTResponse(access_token=generate_token(user.id))


@router.post("/ws-token", response_model=JWTResponse)
@authenticated
async def get_ws_token(request: Request) -> JWTResponse:
    user_id = request.user.user.id
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return JWTResponse(access_token=generate_ws_token(user_id))
