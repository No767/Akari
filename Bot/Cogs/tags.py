import discord
from discord import app_commands
from discord.ext import commands
from Libs.cache import AkariCache, CommandKeyBuilder
from Libs.utils.redis import memCache
from prisma.models import Tag # type: ignore


class Tags(commands.GroupCog, name="tags"):
    """Commands for tags"""

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    @app_commands.command(name="display")
    async def tagView(self, interaction: discord.Interaction, name: str):
        """Displays the content of a tag

        Args:
            interaction (discord.Interaction): Base interaction
            name (str): Name of the tag
        """
        key = CommandKeyBuilder(id=interaction.guild_id, command="tag display")
        connPool = await memCache.get("main")
        cache = AkariCache(connection_pool=connPool)
        if await cache.cacheExists(key=key) is False:
            tagData = await Tag.prisma().find_first(where={"name": {"contains": name}})
            if tagData is None:
                return await interaction.response.send_message(f"{name} was not found")
            await cache.setBasicCommandCache(key=key, value=tagData.content, ttl=30)
            return await interaction.response.send_message(tagData.content)
        else:
            return await interaction.response.send_message(
                await cache.getBasicCommandCache(key=key)
            )


async def setup(bot):
    await bot.add_cog(Tags(bot))
