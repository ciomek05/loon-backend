from sqlmodel import Session, select

from loon.web.db import engine
from loon.web.users.models import User


def choose_admin(username: str) -> None:
    with Session(engine) as session:
        user = session.exec(
            select(User).where(User.internal_username == username)
        ).first()

        if user is None:
            print(f"No user named {username!r}.")
            return

        if user.admin:
            print(f"{username} is already admin.")
            return

        user.admin = True
        session.add(user)
        session.commit()

        print(f"Promoted {username} to admin.")
