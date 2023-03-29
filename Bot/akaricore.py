import logging

import discord
from anyio import Path
from discord.ext import commands
from Libs.utils.redis import redisCheck


class AkariCore(commands.Bot):
    """Akari's Core - Rebuilt with discord.py"""

    def __init__(
        self,
        intents: discord.Intents,
        command_prefix: str = "~",
        *args,
        **kwargs,
    ) -> None:
        super().__init__(
            intents=intents, command_prefix=command_prefix, *args, **kwargs
        )
        self.logger = logging.getLogger("akaribot")

    async def setup_hook(self) -> None:
        """The setup that is called before the bot is ready"""
        cogsPath = Path(__file__).parent.joinpath("Cogs")
        async for cog in cogsPath.rglob("*.py"):
            self.logger.debug(f"Loaded Cog: {cog.name[:-3]}")
            await self.load_extension(f"Cogs.{cog.name[:-3]}")

        self.loop.create_task(redisCheck())
