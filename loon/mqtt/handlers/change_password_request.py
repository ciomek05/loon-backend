import json

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from loon.web.db import engine
from loon.web.logs.service import write_log
from loon.web.logs.types import LogTypeEnum
from loon.web.users.models import MinecraftUser, User


async def change_password_handler(client, userdata, msg, data):
    prefix = "loon/auth/register/"

    if not msg.topic.startswith(prefix):
        return

    rest = msg.topic[len(prefix):]
    uuid, _, subtopic = rest.partition("/")

    if not uuid or subtopic != "change_password":
        return

    password = data["password"]

    with Session(engine) as session:
        statement = select(User).join(MinecraftUser).where(MinecraftUser.uuid == uuid)
        user = session.exec(statement).first()

        if user is None:
            client.publish(f"loon/auth/change_password/{uuid}/response",
                           json.dumps({"success": False, "error": "The user is not registered!"}))
            return

        user = session.exec(
            select(User).join(MinecraftUser).where(MinecraftUser.uuid == uuid)
        ).first()
        user.password = password
        internal_username = user.internal_username

        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            client.publish(f"loon/auth/change_password/{uuid}/response",
                           json.dumps({"success": False, "error": "The user is not registered!"}))

            return

    await write_log(LogTypeEnum.PLAYER_PASSWORD_CHANGED, f"Player {internal_username} ({uuid}) changed their password.")

    client.publish(f"loon/auth/change_password/{uuid}/response", json.dumps({"success": True, "error": None}))
