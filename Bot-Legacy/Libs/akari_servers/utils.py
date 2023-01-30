from typing import Dict

from akari_cache import AkariCache, commandKeyBuilder
from akari_utils import AkariCM

from .models import AkariServers


class AkariServerUtils:
    """Utils to help with adding the server profile into the DB"""

    def __init__(
        self, uri: str, models: list, redis_host: str, redis_port: int
    ) -> None:
        """Constructor for the `AkariServerUtils` class

        Args:
            uri (str): Connection URI
            models (list): List of Tortoise ORM models
            redis_host (str): Redis Host
            redis_port (int): Redis Port
        """
        self.self = self
        self.uri = uri
        self.models = models
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.cache = AkariCache(host=self.redis_host, port=self.redis_port)

    async def cacheGuild(self, guild_id: int, command_name: str) -> Dict:
        """Abstraction for caching guild data

        The purpose of this is a helper coroutine that caches the guild data if not cached.
        If cached, it will return the cached data.

        Args:
            guild_id (int): The guild to cache
            command_name (str): Command name. This is used to set up the cache key on Redis

        Returns:
            Dict: This will return the cached data if cached, else it will return the data from the DB
        """
        key = commandKeyBuilder(
            prefix="cache",
            namespace="akari",
            guild_id=guild_id,
            command=f"{command_name}".replace(" ", "-"),
        )
        if await self.cache.cacheExists(key=key) is False:
            async with AkariCM(uri=self.uri, models=self.models):
                guildData = (
                    await AkariServers.filter(guild_id=guild_id).first().values()
                )
                await self.cache.setCommandCacheDict(key=key, value=guildData, ttl=60)
                return guildData
        else:
            return await self.cache.getCommandCacheDict(key=key)
