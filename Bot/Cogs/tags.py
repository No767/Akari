import logging

import discord
from discord import app_commands
from discord.ext import commands
from Libs.utils.redis import memCache


class Tags(commands.GroupCog, name="tags"):
    """Commands for tags"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__()
        self.logger = logging.getLogger("discord")

    @app_commands.command(name="tag")
    async def tags(self, interaction: discord.Interaction):
        """Tags Test

        Args:
            interaction (discord.Interaction): Base interaction
        """
        res = await memCache.get("main")
        self.logger.info(type(res))
        await interaction.response.send_message("Test", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Tags(bot))
