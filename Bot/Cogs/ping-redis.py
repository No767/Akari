import logging
import os
from typing import Union

import redis.asyncio as redis
from aiocache import Cache
from discord.ext import commands, tasks
from dotenv import load_dotenv
from redis.asyncio.connection import Connection, ConnectionPool
from redis.exceptions import ConnectionError, TimeoutError

load_dotenv()

REDIS_HOST = os.environ["REDIS_HOST"]
REDIS_PORT = os.environ["REDIS_PORT"]


class PingRedis(commands.Cog):
    """Starts up the initial connect to the Redis server"""

    def __init__(self):
        self.firstTime = True
        self.logger = logging.getLogger("discord")

    async def cog_load(self) -> None:
        self.pingRedis.add_exception_type(ConnectionError)
        self.pingRedis.add_exception_type(TimeoutError)
        self.pingRedis.start()

    async def cog_unload(self) -> None:
        self.pingRedis.stop()

    async def setupRedisConnPool(self, key: str = "main") -> None:
        """Sets up the Redis connection pool"""
        conn = Connection(
            host=REDIS_HOST,
            port=int(REDIS_PORT),
            db=0,
            socket_timeout=5.0,
            socket_connect_timeout=5.0,
        )
        memCache = Cache()
        await memCache.add(key=key, value=ConnectionPool(connection_class=conn))  # type: ignore
        if self.firstTime:
            self.firstTime = False
            self.logger.info(
                "Successfully saved Redis connection pool to internal cache"
            )

    async def pingRedisServer(
        self, connection_pool: Union[ConnectionPool, None]
    ) -> bool:
        """Pings Redis to make sure it is alive
        Args:
            connection_pool (Union[ConnectionPool, None]): ConnectionPool object to use
        """
        r: redis.Redis = redis.Redis(connection_pool=connection_pool)
        res = await r.ping()
        isServerUp = True if res == b"PONG" or "PONG" else False
        return isServerUp

    @tasks.loop(count=1)
    async def pingRedis(self):
        """Pings Redis to make sure it is alive

        Raises:
            ConnectionError: If the Redis server is not up
        """
        memCache = Cache()
        await self.setupRedisConnPool()
        res = await self.pingRedisServer(connection_pool=await memCache.get(key="main"))
        if res is True:
            self.logger.info("Successfully connected to Redis server")
        else:
            self.logger.error("Failed to connect to Redis server")
            raise ConnectionError

    @pingRedis.error
    async def pingError(self, error):
        self.logger.error(f"Failed to connect to Redis server")
        self.pingRedis.restart()


async def setup(bot) -> None:
    await bot.add_cog(PingRedis())