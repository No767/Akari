import os
import urllib.parse

import discord
from akari_cache import AkariCache, commandKeyBuilder
from akari_servers import AkariServers, AkariServerUtils
from akari_utils import AkariCM
from discord.commands import SlashCommandGroup
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
MODELS = ["akari_modmail.models", "akari_servers.models"]

cache = AkariCache(host=REDIS_HOST, port=REDIS_PORT)
serverUtils = AkariServerUtils(uri=CONNECTION_URI, models=MODELS)


class ModMail(commands.Cog):
    """Akari's Modmail system - Message the mods about something"""

    def __init__(self, bot):
        self.bot = bot

    modmail = SlashCommandGroup(
        "modmail", "Message the mods about something", guild_ids=[970159505390325842]
    )

    # TODO: Set up the setup system
    # One dropdown to handle for who to add to the modmail
    # another for channel
    # @modmail.command("setup")
    # async def setupModMail(self, ctx: discord.ApplicationContext):
    #     """Set up the modmail system"""

    @modmail.command(name="report")
    async def reportMail(self, ctx: discord.ApplicationContext):
        """Adds a report to the modmail"""
        key = commandKeyBuilder(
            prefix="cache",
            namespace="akari",
            guild_id=ctx.guild.id,
            command=f"{ctx.command.qualified_name}".replace(" ", "-"),
        )
        guildData = {}
        if await cache.cacheExists(key=key) is False:
            async with AkariCM(uri=CONNECTION_URI, models=MODELS):
                guildData = (
                    await AkariServers.filter(guild_id=ctx.guild.id).first().values()
                )
                await cache.setCommandCache(key=key, value=guildData, ttl=60)
        else:
            guildData = await cache.getCommandCache(key=key)

        if guildData["modmail"] is False or None:
            await ctx.respond("Modmail is not enabled for this server!")
        else:
            await ctx.respond("Modmail modal here")


def setup(bot):
    bot.add_cog(ModMail(bot))
