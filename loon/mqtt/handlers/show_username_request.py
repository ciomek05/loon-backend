import json

from sqlmodel import Session, select

from loon.web.db import engine
from loon.web.users.models import User


async def show_username_handler(client, userdata, msg, data):
    prefix = "loon/auth/show_username/"

    if not msg.topic.startswith(prefix):
        return

    rest = msg.topic[len(prefix):]
    uuid, _, subtopic = rest.partition("/")

    if not uuid or subtopic:
        return

    with Session(engine) as session:
        user = session.exec(select(User).where(User.uuid == uuid)).first()

        if user is None:
            client.publish(f"loon/auth/show_username/{uuid}/response",
                           json.dumps({"success": False, "error": "The user is not registered!"}))
            return

        internal_username = user.internal_username

    client.publish(f"loon/auth/show_username/{uuid}/response",
                   json.dumps({"success": True, "error": None, "internalUsername": internal_username}))
