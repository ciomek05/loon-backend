from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from loon.web.db import Base


class MinecraftUser(Base):
    __tablename__ = "minecraftuser"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str]
    user: Mapped["User"] = relationship(back_populates="minecraft_user")


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)

    minecraft_user_id: Mapped[int] = mapped_column(ForeignKey("minecraftuser.id"), unique=True)
    minecraft_user: Mapped[MinecraftUser] = relationship(back_populates="user")

    internal_username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    admin: Mapped[bool] = mapped_column(default=False)

    @property
    def uuid(self) -> str:
        return self.minecraft_user.uuid
