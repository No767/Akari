import os
import urllib.parse

import discord
from akari_cache import AkariCache
from akari_modmail import AkariModMailConfig
from akari_servers import AkariServers, AkariServerUtils
from akari_ui_components import AddModMailReportModal, InitConfirmModMailSetupView
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

    @modmail.command(name="setup")
    async def setupModMail(self, ctx: discord.ApplicationContext):
        """Set up the modmail system"""
        view = InitConfirmModMailSetupView(
            uri=CONNECTION_URI,
            models=MODELS,
            redis_host=REDIS_HOST,
            redis_port=REDIS_PORT,
            command_name=ctx.command.qualified_name,
            guild=ctx.guild,
        )
        await ctx.respond("yes", view=view)

    @modmail.command(name="enable")
    async def enableModMail(self, ctx: discord.ApplicationContext):
        """Enable the modmail system if it is disabled"""
        async with AkariCM(uri=self.uri, models=self.models):
            modMailConfig = await AkariModMailConfig.filter(
                guild_id=ctx.guild.id
            ).exists()
            serverConfig = (
                await AkariServers.filter(guild_id=ctx.guild.id).first().values()
            )
            if modMailConfig is False:
                return await ctx.respond(
                    "Akari's ModMail is not set up for this server! Please run `/modmail setup` in order to set up the modmail system!"
                )
            elif modMailConfig is True and serverConfig["modmail"] is False:
                await AkariServers.filter(guild_id=ctx.guild.id).update(modmail=True)
            await ctx.respond("Akari's ModMail is enabled!")

    @modmail.command(name="disable")
    async def disableModMail(self, ctx: discord.ApplicationContext):
        """Disable Akari's ModMail if it is enabled"""
        async with AkariCM(uri=self.uri, models=self.models):
            modMailConfig = await AkariModMailConfig.filter(
                guild_id=ctx.guild.id
            ).exists()
            serverConfig = (
                await AkariServers.filter(guild_id=ctx.guild.id).first().values()
            )
            if modMailConfig is False:
                return await ctx.respond(
                    "Akari's ModMail is not set up for this server! Please run `/modmail setup` in order to set up the modmail system!"
                )
            elif modMailConfig is True and serverConfig["modmail"] is True:
                await AkariServers.filter(guild_id=ctx.guild.id).update(modmail=False)
            await ctx.respond("Akari's ModMail is disabled!")

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
