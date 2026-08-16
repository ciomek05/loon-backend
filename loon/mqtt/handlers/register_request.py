import json

from sqlmodel import Session, select

from loon.web.db import engine
from loon.web.users.models import User
from loon.web.utils.password import hash_password


async def register_request_handler(client, userdata, msg):
    data = json.loads(msg.payload.decode())

    if msg.topic != "loon/register/request":
        return

    uuid = data["uuid"]
    password = data["password"]
    internal_username = data["internalUsername"]

    with Session(engine) as session:
        statement = select(User).where(User.uuid == uuid)
        user = session.exec(statement).first()

    if user is not None:
        client.publish(f"loon/register/{uuid}/response",
                       json.dumps({"success": False, "error": "The user is already registered!"}))
        return

    with Session(engine) as session:
        user = User(uuid=uuid, password=hash_password(password), internal_username=internal_username, admin=False)
        session.add(user)
        session.commit()

    client.publish(f"loon/register/{uuid}/response", json.dumps({"success": True, "error": None}))