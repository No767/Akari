import asyncio
import logging
from typing import Union

import redis.asyncio as redis
from Libs.cache import akariCPM
from redis.asyncio.connection import ConnectionPool
from redis.exceptions import ConnectionError, TimeoutError

from ..backoff import backoff

logger = logging.getLogger("discord" or __name__)


def setupConnPool() -> ConnectionPool:
    """Sets up the Redis connection pool"""
    return akariCPM.createConnPool()


async def pingRedisServer(connection_pool: Union[ConnectionPool, None]) -> bool:
    """Pings Redis to make sure it is alive
    Args:
        connection_pool (Union[ConnectionPool, None]): ConnectionPool object to use
    """
    r: redis.Redis = redis.Redis(connection_pool=connection_pool)
    res = await r.ping()
    await r.close()
    return res


async def redisCheck(
    backoff_sec: int = 15, backoff_index: int = 0
) -> Union[bool, None]:
    """Coroutine to check whether the Redis server is up or not.

    This is handled recursively believe or not

    Args:
        backoff_sec (int, optional): Default backoff to use. Defaults to 15.
        backoff_index (int, optional): The current index. This will be needed to be passed in order to keep the loop going. Defaults to 0.
    """
    try:
        connPool = akariCPM.getConnPool()
        pingRedis = await pingRedisServer(connection_pool=connPool)
        if backoff_index >= 5:
            logger.error("Unable to connect to Redis server")
            return False
        if pingRedis is True:
            logger.info("Sucessfully connected to Redis server")
            return True
    except (ConnectionError, TimeoutError):
        backoffTime = backoff(backoff_sec=backoff_sec, backoff_sec_index=backoff_index)
        logger.error(
            f"Failed to connect to Redis server - Restarting connection in {int(backoffTime)} seconds"
        )
        await asyncio.sleep(backoffTime)
        await redisCheck(
            backoff_index=backoff_index + 1,
        )
