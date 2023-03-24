import asyncio
import logging
from typing import Union

import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool

from ..backoff import backoff
from .cache_obj import memCache
from .gconn import akariCP

logger = logging.getLogger("discord")


def setupConnPool() -> ConnectionPool:
    """Sets up the Redis connection pool"""
    return akariCP.createConnPool()


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


async def redisCheck(backoff_sec: int = 15, backoff_index: int = 0) -> None:
    """Coroutine to check whether the Redis server is up or not.

    This is handled recursively believe or not

    Args:
        backoff_sec (int, optional): Default backoff to use. Defaults to 15.
        backoff_index (int, optional): The current index. This will be needed to be passed in order to keep the loop going. Defaults to 0.
    """
    try:
        connPool = akariCP.getConnPool()
        pingRedis = pingRedisServer(connection_pool=connPool)
        if pingRedis is True:
            logger.info("Sucessfully connected to Redis server")
    except TimeoutError:
        backoffTime = backoff(backoff_sec=backoff_sec, backoff_sec_index=backoff_index)
        logger.error(
            f"Failed to connect to Redis server - Restarting connection in {int(backoffTime)} seconds"
        )
        await asyncio.sleep(backoffTime)
        await redisCheck(
            backoff_sec=backoff_sec,
            backoff_index=backoff_index + 1,
        )
