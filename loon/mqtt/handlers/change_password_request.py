import json

from sqlmodel import Session, select

from loon.web.db import engine
from loon.web.users.models import User
from loon.web.utils.password import hash_password


async def change_password_handler(client, userdata, msg, data):
    if msg.topic != "loon/register/change_password":
        return

    uuid = data["uuid"]
    password = data["password"]

    with Session(engine) as session:
        statement = select(User).where(User.uuid == uuid)
        user = session.exec(statement).first()

    if user is None:
        client.publish(f"loon/register/{uuid}/response",
                       json.dumps({"success": False, "error": "The user is not registered!"}))
        return

    with Session(engine) as session:
        user = session.exec(
            select(User).where(User.uuid == uuid)
        ).first()
        user.password = hash_password(password)
        session.commit()

    client.publish(f"loon/register/{uuid}/response", json.dumps({"success": True, "error": None}))