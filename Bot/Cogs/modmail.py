import os
import urllib.parse

import discord
from akari_cache import AkariCache
from akari_servers import AkariServerUtils
from akari_ui_components import AddModMailReportModal
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
serverUtils = AkariServerUtils(
    uri=CONNECTION_URI, models=MODELS, redis_host=REDIS_HOST, redis_port=REDIS_PORT
)


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
    # Data will have to be stored in a DB somewhere, and cached
    # @modmail.command("setup")
    # async def setupModMail(self, ctx: discord.ApplicationContext):
    #     """Set up the modmail system"""

    @modmail.command(name="report")
    async def reportMail(self, ctx: discord.ApplicationContext):
        """Adds a report to the modmail"""
        guildData = await serverUtils.cacheGuild(
            guild_id=ctx.guild.id, command_name=ctx.command.qualified_name
        )
        if bool(int(guildData["modmail"])) is False:
            await ctx.respond(
                "Sorry, but it seems like ModMail hasn't been set up yet. Please contact your server administrators or staff to set it up."
            )
        else:
            mainModal = AddModMailReportModal(
                uri=CONNECTION_URI, models=MODELS, title="File a mod report"
            )
            await ctx.send_modal(mainModal)


def setup(bot):
    bot.add_cog(ModMail(bot))
