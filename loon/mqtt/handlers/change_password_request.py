import json

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from loon.web.db import engine
from loon.web.users.models import User


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
        statement = select(User).where(User.uuid == uuid)
        user = session.exec(statement).first()

        if user is None:
            client.publish(f"loon/auth/change_password/{uuid}/response",
                           json.dumps({"success": False, "error": "The user is not registered!"}))
            return

        user = session.exec(
            select(User).where(User.uuid == uuid)
        ).first()
        user.password = password

        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            client.publish(f"loon/auth/change_password/{uuid}/response",
                           json.dumps({"success": False, "error": "The user is not registered!"}))

            return

    client.publish(f"loon/auth/change_password/{uuid}/response", json.dumps({"success": True, "error": None}))
