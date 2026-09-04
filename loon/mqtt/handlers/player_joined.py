from loon.web.users.service import sync_minecraft_users


async def player_joined_handler(client, userdata, msg, data):
    if msg.topic != "loon/playerlist/joined":
        return

    player = data.get("player")
    if not player:
        return

    await sync_minecraft_users([{"uuid": player["uuid"], "username": player["username"]}])
