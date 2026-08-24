from pydantic import BaseModel, Field


class JWTRequest(BaseModel):
    username: str
    password: str = Field(max_length=256)


class JWTResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
