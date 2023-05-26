import discord
from discord.ext import commands
from prisma.models import Guild  # type: ignore


class Events(commands.Cog):
    """Events handler"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        """When the bot joins a guild"""
        doesGuildExist = await Guild.prisma().count(where={"id": guild.id}) == 1
        if doesGuildExist is False:
            await Guild.prisma().create(data={"id": guild.id, "name": guild.name})


async def setup(bot):
    await bot.add_cog(Events(bot))
