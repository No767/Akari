import os
import urllib.parse

import discord
from akari_servers import AkariServers
from akari_utils import AkariCM
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("Redis_Host")
REDIS_PORT = os.getenv("Redis_Port")
POSTGRES_USER = os.getenv("Postgres_User")
POSTGRES_PASSWORD = urllib.parse.quote_plus(os.getenv("Postgres_Password"))
POSTGRES_HOST = os.getenv("Postgres_Host")
POSTGRES_PORT = os.getenv("Postgres_Port")
POSTGRES_DB = os.getenv("Postgres_Akari_DB")
CONNECTION_URI = f"asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
MODELS = ["akari_servers.models"]


class ServerSetup(commands.Cog):
    """Server config cog to handle config setup"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """Event listener for when the bot joins a server"""
        async with AkariCM(uri=CONNECTION_URI, models=MODELS):
            res = await AkariServers.exists(guild_id=guild.id)
            if res is False:
                await AkariServers(
                    guild_id=guild.id,
                    admin_logs=True,
                    modmail=False,
                    suggestions=False,
                    tags=True,
                ).save()


def setup(bot):
    bot.add_cog(ServerSetup(bot))
