from pydantic import BaseModel, ConfigDict


class MinecraftUserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    username: str


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    internal_username: str
    admin: bool
    minecraft_user: MinecraftUserPublic
