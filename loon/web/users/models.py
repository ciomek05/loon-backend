from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    uuid: str = Field(unique=True)
    internal_username: str
    password: str
    admin: bool = Field(default=False)
