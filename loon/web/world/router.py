import json

import redis
from fastapi import APIRouter, Request, HTTPException
from starlette import status

from config import settings
from loon.redis.chunk import get_chunks_cache, reset_chunk_cache
from loon.web import get_mqtt_manager
from loon.web.auth.middleware import authenticated
from loon.web.users.state import user_threads, user_world_requests


MAX_CHUNK_COUNT = 100 # TODO: add limit per user requested chunks at once, not per request


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
    chunk_count = (abs(x_end - x_start) + 1) * (abs(z_end - z_start) + 1)
    if chunk_count > MAX_CHUNK_COUNT:
        raise HTTPException(status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                            detail=f"The rectangle is too big. The limit is {MAX_CHUNK_COUNT} per request. ")

    uuid = request.user.user.uuid
    wanted = user_world_requests.get(uuid)

    if not settings.redis.enabled:
        if wanted is not None:
            for x in range(x_start, x_end + 1):
                for z in range(z_start, z_end + 1):
                    wanted.add((x, z))

        get_mqtt_manager().publish(f"loon/world/chunks/{x_start}:{x_end}/{z_start}:{z_end}/request")
        return 200

    misses = []
    thread = user_threads.get(uuid)

    all_coords = [
        (x, z)
        for x in range(x_start, x_end + 1)
        for z in range(z_start, z_end + 1)
    ]

    try:
        hits = await get_chunks_cache(all_coords)
    except redis.exceptions.RedisError:
        if wanted is not None:
            wanted.update(all_coords)

        get_mqtt_manager().publish(f"loon/world/chunks/{x_start}:{x_end}/{z_start}:{z_end}/request")
        return 200

    for coord in all_coords:
        cached_chunk = hits.get(coord)

        if cached_chunk is not None:
            if thread:
                x, z = coord
                await thread.put(
                    json.dumps({"topic": f"world/chunk/{x}/{z}", "payload": cached_chunk})
                )
        else:
            if wanted is not None:
                wanted.add(coord)
            misses.append(coord)

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

