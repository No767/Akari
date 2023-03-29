from typing import Any, Dict, Optional, Union

import ormsgpack
import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool

from .key_builder import CommandKeyBuilder


class AkariCache:
    """Akari's custom caching library. Uses Redis as the backend"""

    def __init__(self, connection_pool: Union[ConnectionPool, None]) -> None:
        """Akari's custom caching library. Uses Redis as the backend

        Args:
            connection_pool (Union[ConnectionPool, None]): Connection Pool object used for Redis
        """
        if connection_pool is None:
            self.connection_pool = ConnectionPool.from_url("redis://localhost:6379/0")
        self.connection_pool = connection_pool

    async def setBasicCache(
        self,
        key: Optional[str],
        value: Union[str, bytes],
        ttl: Optional[int] = 5,
    ) -> None:
        """Sets the command cache on Redis

        Args:
            key (Optional[str]): The key to use for Redis
            value (Union[str, bytes]): The value of the key-pair value
            ttl (Optional[int], optional): TTL of the key-value pair. Defaults to 5.
        """
        if key is None:
            key = CommandKeyBuilder()
        client: redis.Redis = redis.Redis(
            connection_pool=self.connection_pool, auto_close_connection_pool=False
        )
        await client.set(name=key, value=ormsgpack.packb(value), ex=ttl)
        await client.close(close_connection_pool=False)

    async def getBasicCache(self, key: str) -> Union[str, None]:
        """Gets the command cache on Redis

        Args:
            key (str): The key of the key-value pair to get

        Returns:
            str: The value of the key-value pair
        """
        client: redis.Redis = redis.Redis(
            connection_pool=self.connection_pool, auto_close_connection_pool=False
        )
        value: Union[str, None] = await client.get(name=key)
        await client.close(close_connection_pool=False)
        if value is None:
            return None
        return ormsgpack.unpackb(value)

    async def setJSONCache(self, key: str, value: Dict[str, Any], ttl: int = 5) -> None:
        """Sets the JSON cache on Redis

        Args:
            key (str): The key to use for Redis
            value (Dict[str, Any]): The value of the key-pair value
            ttl (Optional[int], optional): TTL of the key-value pair. Defaults to 5.
        """
        client: redis.Redis = redis.Redis(
            connection_pool=self.connection_pool, auto_close_connection_pool=False
        )
        await client.json().set(name=key, path="$", obj=value)
        await client.expire(name=key, time=ttl)
        await client.close(close_connection_pool=False)

    async def getJSONCache(self, key: str) -> Union[str, None]:
        """Gets the JSON cache on Redis

        Args:
            key (str): The key of the key-value pair to get

        Returns:
            Dict[str, Any]: The value of the key-value pair
        """
        client: redis.Redis = redis.Redis(
            connection_pool=self.connection_pool, auto_close_connection_pool=False
        )
        value = await client.json().get(name=key)
        await client.close(close_connection_pool=False)
        if value is None:
            return None
        return value

    async def cacheExists(self, key: str) -> bool:
        """Checks to make sure if the cache exists

        Args:
            key (str): Redis key to check

        Returns:
            bool: Whether the key exists or not
        """
        client: redis.Redis = redis.Redis(
            connection_pool=self.connection_pool, auto_close_connection_pool=False
        )
        keyExists = await client.exists(key) >= 1
        await client.close(close_connection_pool=False)
        return True if keyExists else False
