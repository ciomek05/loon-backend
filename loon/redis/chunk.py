import json

from config import settings
from loon.redis import r


async def set_chunk_cache(x: int, z: int, chunk_payload):
    await r.setex(f'{x}:{z}', settings.redis.expire_time, str(json.dumps(chunk_payload)))

async def get_chunk_cache(x: int, z: int):
    chunk = await r.get(f'{x}:{z}')

    if chunk:
        return json.loads(chunk)

    return None

async def get_chunks_cache(coords):
    if not coords:
        return {}

    vals = await r.mget([f'{x}:{z}' for x, z in coords])
    return {c: json.loads(v) for c, v in zip(coords, vals) if v}

async def reset_chunk_cache(x: int, z: int):
    return await r.delete(f'{x}:{z}')
