from sqlmodel import SQLModel, Field, Relationship


class MinecraftUser(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    uuid: str = Field(unique=True)
    username: str
    user: "User" = Relationship(back_populates="minecraft_user")


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)

    minecraft_user_id: int = Field(foreign_key="minecraftuser.id", nullable=False, unique=True)
    minecraft_user: MinecraftUser = Relationship(back_populates="user")

    internal_username: str = Field(unique=True)
    password: str
    admin: bool = Field(default=False)

    @property
    def uuid(self) -> str:
        return self.minecraft_user.uuid
