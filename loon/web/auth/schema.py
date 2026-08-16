from pydantic import BaseModel


class JWTRequest(BaseModel):
    username: str
    password: str


class JWTResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
