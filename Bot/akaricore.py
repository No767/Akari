import asyncio
import logging
import random
from typing import Optional

import discord
from aiocache import Cache
from anyio import Path
from discord.ext import commands
from Libs.utils.redis import pingRedisServer, setupRedisConnPool
from prisma import Prisma
from prisma.engine.errors import EngineConnectionError
from redis.exceptions import ConnectionError, TimeoutError


class AkariCore(commands.Bot):
    """Akari's Core - Rebuilt with discord.py"""

    def __init__(
        self,
        intents: discord.Intents,
        command_prefix: str = "!",
        testing_guild_id: Optional[int] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(
            intents=intents, command_prefix=command_prefix, *args, **kwargs
        )
        self.testing_guild_id: Optional[int] = testing_guild_id
        self.logger = logging.getLogger("akaribot")
        self.backoffSec = 5
        self.backoffSecIndex = 0

    def _backoff(self) -> float:
        sleepAmt = self.backoffSec * 2**self.backoffSecIndex + random.uniform(  # nosec
            0, 1
        )  # nosec
        if sleepAmt > 60:
            return 60
        return sleepAmt

    async def redisCheck(self) -> None:
        try:
            memCache = Cache()
            await setupRedisConnPool()
            res = await pingRedisServer(connection_pool=await memCache.get(key="main"))
            if res is True:
                self.logger.info("Successfully connected to Redis server")
        except ConnectionError:
            backOffTime = self._backoff()
            self.logger.error(
                f"Failed to connect to Redis server - Reconnecting in {int(backOffTime)} seconds"
            )
            await asyncio.sleep(self._backoff())
            self.backoffSecIndex += 1
            await self.redisCheck()
        except TimeoutError:
            backOffTime = self._backoff()
            self.logger.error(
                f"Connection timed out - Reconnecting in {int(backOffTime)} seconds"
            )
            await asyncio.sleep(backOffTime)
            self.backoffSecIndex += 1
            await self.redisCheck()

    async def connectDB(self) -> None:
        try:
            db = Prisma(auto_register=True)
            await db.connect()
            self.logger.info("Successfully connected to DB")
        except EngineConnectionError:
            self.logger.error("Failed to connect to DB")

    async def setup_hook(self) -> None:
        """The setup that is called before the bot is ready"""
        cogsPath = Path(__file__).parent.joinpath("Cogs")
        async for cog in cogsPath.rglob("*.py"):
            self.logger.debug(f"Loaded Cog: {cog.name[:-3]}")
            await self.load_extension(f"Cogs.{cog.name[:-3]}")

        self.loop.create_task(self.connectDB())
        self.loop.create_task(self.redisCheck())

        if self.testing_guild_id:
            guild = discord.Object(self.testing_guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
