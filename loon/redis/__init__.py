import redis
from redis.backoff import ExponentialBackoff
from redis.exceptions import ConnectionError, TimeoutError
from redis.retry import Retry

from config import settings

r: redis.Redis | None = None
if not settings.redis.enabled:
    r = None
else:
    r = redis.Redis(
        host=settings.redis.host,
        port=settings.redis.port,
        password=settings.redis.password,
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2,
        socket_keepalive=True,
        health_check_interval=30,
        retry_on_timeout=True,
        retry=Retry(ExponentialBackoff(cap=10, base=0.5), retries=0),
        retry_on_error=[ConnectionError, TimeoutError],
    )
