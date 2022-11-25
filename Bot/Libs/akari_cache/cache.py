import asyncio
from typing import Optional, Union

import orjson
import uvloop
from coredis import Redis

from .key_builder import commandKeyBuilder


class AkariCache:
    """Akari's custom caching library. Uses Redis as the backend for caching"""

    def __init__(self, host: str = "127.0.0.1", port: int = 6379) -> None:
        """Constructor for `AkariCache`

        Args:
            host (str, optional): Redis Server Host. Defaults to "127.0.0.1".
            port (int, optional): Redis Server Port. Defaults to 6379.
        """
        self.self = self
        self.host = host
        self.port = port

    async def setCommandCache(
        self,
        key: Optional[str] = commandKeyBuilder(
            prefix="cache", namespace="akari", guild_id=None, command=None
        ),
        value: Union[str, bytes, dict] = None,
        ttl: Optional[int] = 30,
    ) -> None:
        """Sets the command cache on Redis

        Args:
            key (Optional[str], optional): Key to set on Redis. Defaults to `commandKeyBuilder(prefix="akari", namespace="cache", user_id=None, command=None)`.
            value (Union[str, bytes, dict]): Value to set on Redis. Defaults to None.
            ttl (Optional[int], optional): TTL for the key-value pair. Defaults to 30.
        """
        conn = Redis(host=self.host, port=self.port)
        await conn.set(key=key, value=orjson.dumps(value), ex=ttl)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    async def getCommandCache(self, key: str) -> str:
        """Gets the command cache from Redis

        Args:
            key (str): Key to get from Redis
        """
        conn = Redis(host=self.host, port=self.port)
        return orjson.loads(await conn.get(key))

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    async def cacheExists(self, key: str) -> bool:
        """Checks if the key exists or not

        Args:
            key (str): The key to check against

        Returns:
            bool: If the key exists or not
        """
        conn = Redis(host=self.host, port=self.port)
        data = await conn.exists([key])
        return True if data >= 1 else False

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    async def setCommandCacheDict(
        self,
        key: Optional[str] = commandKeyBuilder(
            prefix="cache", namespace="akari", guild_id=None, command=None
        ),
        value: Union[str, bytes, dict] = None,
        ttl: Optional[int] = 30,
    ):
        """Sets up the command cache, but this time with an HSET, not a regular set

        Args:
            key (Optional[str], optional): Redis key. Defaults to commandKeyBuilder( prefix="cache", namespace="akari", guild_id=None, command=None ).
            value (Union[str, bytes, dict], optional): The value to set to. Ideally should be a `Dict`. Defaults to None.
            ttl (Optional[int], optional): How long the key-value pair lasts for. Defaults to 30.
        """
        conn = Redis(host=self.host, port=self.port, decode_responses=True)
        await conn.hset(key=key, field_values=value)
        await conn.expire(key=key, seconds=ttl)

    async def getCommandCacheDict(self, key: str):
        """Gets the command cache from Redis

        Args:
            key (str): Key to get from Redis
        """
        conn = Redis(host=self.host, port=self.port, decode_responses=True)
        return await conn.hgetall(key=key)
