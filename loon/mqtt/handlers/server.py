import json

from loon.web.users.state import user_threads


async def server_handler(client, userdata, msg, data):
    if msg.topic != "loon/server/info":
        return

    envelope = json.dumps({"topic": "server/info", "payload": data})

    for queue in list(user_threads.values()):
        await queue.put(envelope)
