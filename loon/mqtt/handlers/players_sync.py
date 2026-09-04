from loon.web.users.service import sync_minecraft_users


async def players_sync_handler(client, userdata, msg, data):
    if msg.topic != "loon/playerlist/sync":
        return

    await sync_minecraft_users(data.get("players", []))
