import json

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from loon.web.db import engine
from loon.web.logs.service import write_log
from loon.web.logs.types import LogTypeEnum
from loon.web.users.models import MinecraftUser, User
from loon.web.users.service import sync_minecraft_users


async def register_request_handler(client, userdata, msg, data):
    prefix = "loon/auth/register/"

    if not msg.topic.startswith(prefix):
        return

    rest = msg.topic[len(prefix):]
    uuid, _, subtopic = rest.partition("/")

    if not uuid or subtopic != "request":
        return

    password = data["password"]
    internal_username = data["internalUsername"]
    username = data["username"]

    await sync_minecraft_users([{"uuid": uuid, "username": username}])

    with Session(engine) as session:
        minecraft_user = session.exec(select(MinecraftUser).where(MinecraftUser.uuid == uuid)).first()

        statement = select(User).where(User.minecraft_user_id == minecraft_user.id)
        user = session.exec(statement).first()

        if user is not None:
            client.publish(f"loon/auth/register/{uuid}/response",
                           json.dumps({"success": False, "error": "The user is already registered!"}))
            return

        statement = select(User).where(User.internal_username == internal_username)
        user = session.exec(statement).first()

        if user is not None:
            client.publish(f"loon/auth/register/{uuid}/response",
                           json.dumps({"success": False, "error": f"The {internal_username} is taken!"}))
            return

        user = User(minecraft_user_id=minecraft_user.id, password=password, internal_username=internal_username, admin=False)
        session.add(user)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            client.publish(f"loon/auth/register/{uuid}/response",
                           json.dumps({"success": False, "error": "The user is already registered!"}))

            return

    await write_log(LogTypeEnum.PLAYER_REGISTERED, f"Player {internal_username} ({uuid}) registered.")

    client.publish(f"loon/auth/register/{uuid}/response", json.dumps({"success": True, "error": None}))
