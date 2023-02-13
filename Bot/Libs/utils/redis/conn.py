from typing import Union

import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool

from .cache_obj import memCache


async def setupRedisConnPool(
    redis_host: str = "localhost", redis_port: int = 6379, key: str = "main"
) -> None:
    """Sets up the Redis connection pool

    Args:
        redis_host (str): Redis Host to connect to
        redis_port (int): Redis Port to connect to
        key (str): Key to store the connection pool object into memory
    """
    await memCache.add(key=key, value=ConnectionPool.from_url(f"redis://{redis_host}:{redis_port}/0"))  # type: ignore


async def pingRedisServer(connection_pool: Union[ConnectionPool, None]) -> bool:
    """Pings Redis to make sure it is alive
    Args:
        connection_pool (Union[ConnectionPool, None]): ConnectionPool object to use
    """
    r: redis.Redis = redis.Redis(connection_pool=connection_pool)
    res = await r.ping()
    isServerUp = True if res == b"PONG" or "PONG" else False
    return isServerUp
