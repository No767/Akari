import asyncio
from typing import Optional, Union

import uvloop
from coredis import Redis

from .key_builder import commandKeyBuilder


class AkariCache:
    """Akari's custom caching library. Uses Redis as the backend for caching"""

    def __init__(self, url: str):
        """Constructor for `AkariCache`

        Args:
            url (str): Redis Connection URL
        """
        self.self = self
        self.url = url

    async def setCommandCache(
        self,
        key: Optional[str] = commandKeyBuilder(
            prefix="cache", namespace="akari", guild_id=None, command=None
        ),
        value: Union[str, bytes] = None,
        ttl: Optional[int] = 30,
    ) -> None:
        """Sets the command cache on Redis

        Args:
            key (Optional[str], optional): Key to set on Redis. Defaults to `commandKeyBuilder(prefix="adachi", namespace="cache", user_id=None, command=None)`.
            value (Union[str, bytes]): Value to set on Redis. Defaults to None.
            ttl (Optional[int], optional): TTL for the key-value pair. Defaults to 30.
        """
        conn = Redis.from_url(self.url)
        await conn.set(key=key, value=value, ex=ttl)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    async def getCommandCache(self, key: str) -> str:
        """Gets the command cache from Redis

        Args:
            key (str): Key to get from Redis
        """
        conn = Redis.from_url(self.url)
        return await conn.get(key)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    async def cacheExists(self, key: str) -> bool:
        """Checks if the key exists or not

        Args:
            key (str): The key to check against

        Returns:
            bool: If the key exists or not
        """
        conn = Redis.from_url(self.url)
        data = await conn.exists([key])
        return True if data >= 1 else False

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
