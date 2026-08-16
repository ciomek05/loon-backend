import json
import re

import redis

from config import settings
from loon.redis.chunk import set_chunk_cache
from loon.web.users.state import user_threads, user_world_requests


async def world_handler(client, userdata, msg):
    chunk_topic = re.compile(r"^loon/world/chunk/(-?\d+)/(-?\d+)$")

    match = chunk_topic.match(msg.topic)

    if not match:
        return

    try:
        data = json.loads(msg.payload.decode())
    except json.JSONDecodeError:
        return

    x, z = int(match.group(1)), int(match.group(2))
    envelope = json.dumps({"topic": f"world/chunk/{x}/{z}", "payload": data})
    coord = (x, z)

    if settings.redis.enabled:
        try:
            set_chunk_cache(x, z, data)
        except redis.RedisError:
            pass

    for uuid, queue in list(user_threads.items()):
        wanted = user_world_requests.get(uuid)
        if not wanted or coord not in wanted:
            continue
        await queue.put(envelope)
        wanted.discard(coord)
