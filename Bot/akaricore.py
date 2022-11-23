import logging
import os
import sys
from pathlib import Path

import discord

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] | %(asctime)s >> %(message)s",
    datefmt="[%m/%d/%Y] [%I:%M:%S %p %Z]",
)

logging.getLogger("tortoise").setLevel(logging.WARNING)


basePath = Path(__file__).parents[0].absolute()
libPath = os.path.join(str(basePath), "Bot", "Libs")
sys.path.append(str(libPath))


class AkariCore(discord.Bot):
    """The core of Akari, but this time it's subclassed"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_cogs()

    def load_cogs(self):
        """Akari's system to load cogs"""
        path = Path(__file__).parents[0].absolute()
        cogsPath = os.path.join(str(path), "Cogs")
        for cogs in os.listdir(cogsPath):
            if cogs.endswith(".py"):
                self.load_extension(f"Cogs.{cogs[:-3]}", store=False)

    async def on_ready(self):
        logging.info(f"{self.user.name} is ready!")
        await self.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching, name="/help")
        )
