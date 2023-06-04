import logging
from pathlib import Path as SyncPath

import asyncpg
import discord
from aiohttp import ClientSession
from anyio import Path
from discord.ext import commands
from Libs.utils import ensureOpenConn
from Libs.utils.redis import openConnCheck

# Some weird import logic to ensure that watchfiles is there
_fsw = True
try:
    from watchfiles import awatch
except ImportError:
    _fsw = False


class AkariCore(commands.Bot):
    """Akari's Core - Rebuilt with discord.py"""

    def __init__(
        self,
        intents: discord.Intents,
        session: ClientSession,
        pool: asyncpg.Pool,
        dev_mode: bool = False,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(intents=intents, command_prefix="~", *args, **kwargs)
        self._session = session
        self._pool = pool
        self.dev_mode = dev_mode
        self.logger = logging.getLogger("akaribot")

    @property
    def session(self) -> ClientSession:
        """A global AIOHTTP ClientSession used throughout the lifetime of Akari

        Returns:
            ClientSession: AIOHTTP ClientSession
        """
        return self._session

    @property
    def pool(self) -> asyncpg.Pool:
        """A global connection pool used throughout the lifetime of Akari

        Returns:
            asyncpg.Pool: Asyncpg connection pool
        """
        return self._pool

    async def fsWatcher(self) -> None:
        cogsPath = SyncPath(__file__).parent.joinpath("Cogs")
        async for changes in awatch(cogsPath):
            changesList = list(changes)[0]
            if changesList[0].modified == 2:
                reloadFile = SyncPath(changesList[1])
                self.logger.info(f"Reloading extension: {reloadFile.name[:-3]}")
                await self.reload_extension(f"Cogs.{reloadFile.name[:-3]}")

    async def setup_hook(self) -> None:
        """The setup that is called before the bot is ready"""
        cogsPath = Path(__file__).parent.joinpath("Cogs")
        async for cog in cogsPath.rglob("*.py"):
            self.logger.debug(f"Loaded Cog: {cog.name[:-3]}")
            await self.load_extension(f"Cogs.{cog.name[:-3]}")

        self.loop.create_task(ensureOpenConn(self._pool))
        self.loop.create_task(openConnCheck())
        if self.dev_mode is True and _fsw is True:
            self.logger.info("Dev mode is enabled. Loading Jishaku and FSWatcher")
            self.loop.create_task(self.fsWatcher())
            await self.load_extension("jishaku")
