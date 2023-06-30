import logging

import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool

logger = logging.getLogger("discord" or __name__)


async def openConnCheck(connection_pool: ConnectionPool) -> bool:
    """Pings the Redis server to check if it's open or not

    Args:
        connection_pool (Union[ConnectionPool, None]): The supplied connection pool. If none, it will be created automatically

    Returns:
        bool: Whether the server is up or not
    """
    # Lol I actually wrote this on an flight to Tokyo
    r: redis.Redis = redis.Redis(connection_pool=connection_pool)
    resultPing = await r.ping()
    if resultPing:
        logger.info("Redis server is up")
        return True
    logger.error("Failed to connect to the Redis server - Restart Akari to reconnect")
    return False
