from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session, select

from loon.web.auth.schema import JWTResponse, JWTRequest
from loon.web.db import engine
from loon.web.users.models import User
from loon.web.utils.jwt import generate_token
from loon.web.utils.password import verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/jwt/", response_model=JWTResponse)
async def get_jwt(body: JWTRequest) -> JWTResponse:
    with Session(engine) as session:
        statement = select(User).where(User.internal_username == body.username)
        user = session.exec(statement).first()

        if user is None or not verify_password(body.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        assert user.id is not None
        return JWTResponse(access_token=generate_token(user.id))
