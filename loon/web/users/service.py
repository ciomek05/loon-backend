import asyncio

from sqlalchemy import select
from sqlalchemy.orm import Session

from loon.web.db import engine
from loon.web.users.models import MinecraftUser


def _sync_minecraft_users(players: list[dict]) -> list[MinecraftUser]:
    players_by_uuid = {player["uuid"]: player["username"] for player in players}

    with Session(engine) as session:
        existing = session.execute(
            select(MinecraftUser).where(MinecraftUser.uuid.in_(players_by_uuid))
        ).scalars().all()
        existing_by_uuid = {minecraft_user.uuid: minecraft_user for minecraft_user in existing}

        new_users = []
        for uuid, username in players_by_uuid.items():
            minecraft_user = existing_by_uuid.get(uuid)

            if minecraft_user is None:
                minecraft_user = MinecraftUser(uuid=uuid, username=username)
                new_users.append(minecraft_user)
                session.add(minecraft_user)
            elif minecraft_user.username != username:
                minecraft_user.username = username
                session.add(minecraft_user)

        session.commit()

        minecraft_users = [*existing, *new_users]
        for minecraft_user in minecraft_users:
            session.refresh(minecraft_user)

        return minecraft_users


async def sync_minecraft_users(players: list[dict]) -> list[MinecraftUser]:
    if not players:
        return []

    return await asyncio.to_thread(_sync_minecraft_users, players)
