from typing import Any, Dict, Optional, Union

import ormsgpack
import redis.asyncio as redis
from cache.key_builder import CommandKeyBuilder
from redis.asyncio.connection import ConnectionPool


class AkariCache:
    """Akari's custom caching library. Uses Redis as the backend"""

    def __init__(self, connection_pool: ConnectionPool) -> None:
        """Akari's custom caching library. Uses Redis as the backend

        Args:
            connection_pool (ConnectionPool): Connection Pool object used for Redis
        """
        self.connection_pool = connection_pool
        self.client: redis.Redis = redis.Redis(connection_pool=self.connection_pool)

    async def setBasicCommandCache(
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
        await self.client.set(name=key, value=ormsgpack.packb(value), ex=ttl)

    async def getBasicCommandCache(self, key: str) -> Union[str, None]:
        """Gets the command cache on Redis

        Args:
            key (str): The key of the key-value pair to get

        Returns:
            str: The value of the key-value pair
        """
        value: Union[str, None] = await self.client.get(name=key)
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
        await self.client.json().set(name=key, path="$", obj=value)
        await self.client.expire(name=key, time=ttl)

    async def getJSONCache(self, key: str) -> Union[str, None]:
        """Gets the JSON cache on Redis

        Args:
            key (str): The key of the key-value pair to get

        Returns:
            Dict[str, Any]: The value of the key-value pair
        """
        value = await self.client.json().get(name=key)
        if value is None:
            return None
        return value
