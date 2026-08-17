import json

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from loon.web.db import engine
from loon.web.users.models import User


async def register_request_handler(client, userdata, msg, data):
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

        statement = select(User).where(User.internal_username == internal_username)
        user = session.exec(statement).first()

        if user is not None:
            client.publish(f"loon/register/{uuid}/response",
                           json.dumps({"success": False, "error": f"The {internal_username} is taken!"}))
            return

        user = User(uuid=uuid, password=password, internal_username=internal_username, admin=False)
        session.add(user)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            client.publish(f"loon/register/{uuid}/response",
                           json.dumps({"success": False, "error": "The user is already registered!"}))

            return

    client.publish(f"loon/register/{uuid}/response", json.dumps({"success": True, "error": None}))