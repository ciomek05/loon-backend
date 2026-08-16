import json

import redis
from fastapi import APIRouter, Request

from config import settings
from loon.redis.chunk import get_chunk_cache, reset_chunk_cache
from loon.web import get_mqtt_manager
from loon.web.auth.middleware import authenticated
from loon.web.users.state import user_threads

router = APIRouter(prefix="/world", tags=["world"])


@router.get("/request")
@authenticated
async def request_world(
    request: Request,
    x_start: int,
    x_end: int,
    z_start: int,
    z_end: int,
):
    if not settings.redis.enabled:
        get_mqtt_manager().publish(f"loon/world/chunks/{x_start}:{x_end}/{z_start}:{z_end}/request")
        return 200

    misses = []
    thread = user_threads.get(request.user.user.uuid)

    try:
        for x in range(x_start, x_end + 1):
            for z in range(z_start, z_end + 1):
                cached_chunk = get_chunk_cache(x, z)

                if cached_chunk is not None:
                    if thread:
                        await thread.put(
                            json.dumps({"topic": f"world/chunk/{x}/{z}", "payload": cached_chunk})
                        )
                else:
                    misses.append((x, z))
    except redis.RedisError as e:
        get_mqtt_manager().publish(f"loon/world/chunks/{x_start}:{x_end}/{z_start}:{z_end}/request")
        return 200

    for xa, xb, za, zb in miss_row_rects(misses):
        get_mqtt_manager().publish(f"loon/world/chunks/{xa}:{xb}/{za}:{zb}/request")

    return 200


def miss_row_rects(misses: list):
    rows = {}

    for x, z in misses:
        if z not in rows:
            rows[z] = []
        rows[z].append(x)

    rects = []

    for z, xs in rows.items():
        xs.sort()

        start = xs[0]
        end = xs[0]

        for x in xs[1:]:
            if x == end + 1:
                end = x
            else:
                rects.append((start, end, z, z))
                start = x
                end = x

        rects.append((start, end, z, z))

    return rects

