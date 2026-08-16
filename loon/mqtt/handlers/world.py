import json
import re

import redis

from config import settings
from loon.redis.chunk import set_chunk_cache
from loon.web.users.state import user_threads


async def world_handler(client, userdata, msg):
    chunk_topic = re.compile(r"^loon/world/chunk/(-?\d+)/(-?\d+)$")

    match = chunk_topic.match(msg.topic)

    if not match:
        return

    try:
        data = json.loads(msg.payload.decode())
    except json.JSONDecodeError:
        return

    x, z = match.group(1), match.group(2)
    envelope = json.dumps({"topic": f"world/chunk/{x}/{z}", "payload": data})

    if settings.redis.enabled:
        try:
            set_chunk_cache(int(x), int(z), data)
        except redis.RedisError:
            pass

    for queue in list(user_threads.values()):
        await queue.put(envelope)
