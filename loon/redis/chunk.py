import json

from config import settings
from loon.redis import r


def set_chunk_cache(x: int, z: int, chunk_payload):
    r.setex(f'{x}:{z}', settings.redis.expire_time, str(json.dumps(chunk_payload)))

def get_chunk_cache(x: int, z: int):
    chunk = r.get(f'{x}:{z}')

    if chunk:
        return json.loads(chunk)

    return None

def reset_chunk_cache(x: int, z: int):
    return r.delete(f'{x}:{z}')
