import json

from loon.web.users.state import user_threads


async def player_handler(client, userdata, msg, data):
    prefix = "loon/player/"

    if not msg.topic.startswith(prefix):
        return

    rest = msg.topic[len(prefix):]
    player_uuid, _, subtopic = rest.partition("/")

    queue = user_threads.get(player_uuid)
    if queue is not None:
        await queue.put(json.dumps({"topic": subtopic, "payload": data}))
