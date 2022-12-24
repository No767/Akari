import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import List

import discord
from discord.ext import tasks
from tortoise import BaseDBAsyncClient, Tortoise, connections
from tortoise.exceptions import DBConnectionError

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

    def __init__(self, uri: str, models: List, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uri = uri
        self.models = models
        self.connected_db = asyncio.Event()
        self.connect_db.add_exception_type(TimeoutError)
        self.connect_db.add_exception_type(DBConnectionError)
        self.connect_db.start()
        self.load_cogs()

    def load_cogs(self):
        """Akari's system to load cogs"""
        path = Path(__file__).parents[0].absolute()
        cogsPath = os.path.join(str(path), "Cogs")
        for cogs in os.listdir(cogsPath):
            if cogs.endswith(".py"):
                self.load_extension(f"Cogs.{cogs[:-3]}", store=False)

    @tasks.loop(count=1)
    async def connect_db(self):
        try:
            await Tortoise.init(db_url=self.uri, modules={"models": self.models})
            conn: BaseDBAsyncClient = connections.get("default")
            await conn.create_connection(with_db=True)
            self.connected_db.set()
            logging.info("Connected to database")
        except TimeoutError:
            logging.error("Failed to connect to PostgreSQL. Retrying in 15 seconds")
            await asyncio.sleep(15)
            self.connect_db.restart()

    @connect_db.after_loop
    async def connTeardown(self):
        if self.connect_db.is_being_cancelled():
            await connections.close_all()

    async def on_ready(self):
        logging.info(f"{self.user.name} is ready!")
        await self.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching, name="/help")
        )
