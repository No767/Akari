from typing import Union

import redis.asyncio as redis
from redis.asyncio.connection import Connection, ConnectionPool

from .cache_obj import memCache


async def setupRedisConnPool(
    redis_host: str = "localhost",
    redis_port: int = 6379,
    key: str = "main",
    timeout: float = 15.0,
) -> None:
    """Sets up the Redis connection pool

    Args:
        redis_host (str): Redis Host to connect to
        redis_port (int): Redis Port to connect to
        key (str): Key to store the connection pool object into memory
        timeout (float): Socket connection timeout
    """
    conn = Connection(host=redis_host, port=redis_port, db=0, socket_timeout=timeout)
    await memCache.add(key=key, value=ConnectionPool(connection_class=conn))  # type: ignore


async def pingRedisServer(connection_pool: Union[ConnectionPool, None]) -> bool:
    """Pings Redis to make sure it is alive
    Args:
        connection_pool (Union[ConnectionPool, None]): ConnectionPool object to use
    """
    r: redis.Redis = redis.Redis(connection_pool=connection_pool)
    res = await r.ping()
    isServerUp = True if res == b"PONG" or "PONG" else False
    return isServerUp
