import datetime
import platform
import time

import discord
from akaricore import AkariCore
from discord import app_commands
from discord.ext import commands
from Libs.utils import Embed

VERSION = "v0-rewrite"


class Akari(commands.GroupCog, name="akari"):
    """Commands to obtain stats about Akari"""

    def __init__(self, bot: AkariCore) -> None:
        self.bot = bot
        super().__init__()

    @commands.Cog.listener()
    async def on_ready(self):
        global startTime
        startTime = time.time()

    @app_commands.command(name="uptime")
    async def uptime(self, interaction: discord.Interaction) -> None:
        """Returns uptime for Akari

        Args:
            interaction (discord.Interaction): Base interaction
        """
        uptime = datetime.timedelta(seconds=int(round(time.time() - startTime)))
        embed = Embed()
        embed.description = f"Akari's Uptime: `{uptime.days} Days, {uptime.seconds//3600} Hours, {(uptime.seconds//60)%60} Minutes, {(uptime.seconds%60)} Seconds`"
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="info")
    async def info(self, interaction: discord.Interaction) -> None:
        """Shows some basic info about Akari

        Args:
            interaction (discord.Interaction): Base interaction
        """
        embed = Embed()
        embed.title = f"{self.bot.user.name} Info"  # type: ignore
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)  # type: ignore
        embed.add_field(name="Server Count", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="User Count", value=len(self.bot.users), inline=True)
        embed.add_field(
            name="Python Version", value=platform.python_version(), inline=True
        )
        embed.add_field(
            name="Discord.py Version", value=discord.__version__, inline=True
        )
        embed.add_field(name="Akari Build Version", value=VERSION, inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="version")
    async def version(self, interaction: discord.Interaction) -> None:
        """Returns the current version of Akari

        Args:
            interaction (discord.Interaction): Base interaction
        """
        embed = Embed()
        embed.description = f"Build Version: {VERSION}"
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ping")
    async def ping(self, interaction: discord.Interaction) -> None:
        """Returns the current latency of Akari

        Args:
            interaction (discord.Interaction): Base interaction
        """
        embed = Embed()
        embed.description = f"Pong! {round(self.bot.latency * 1000)}ms"
        await interaction.response.send_message(embed=embed)


async def setup(bot: AkariCore) -> None:
    await bot.add_cog(Akari(bot))
