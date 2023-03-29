import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import escape_markdown
from Libs.ui.tags import CreateTag, EditTag
from Libs.utils.redis import memCache
from prisma.models import Guild, Tag  # type: ignore

from Bot.Libs.cache import AkariCache, CommandKeyBuilder


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
            tagData = await Tag.prisma().find_first(where={"AND": [{"id": interaction.guild_id}, {"name": {"equals": name}}]})  # type: ignore
            if tagData is None:
                return await interaction.response.send_message(f"{name} was not found")
            await cache.setBasicCommandCache(key=key, value=tagData.content, ttl=30)
            return await interaction.response.send_message(tagData.content)
        else:
            return await interaction.response.send_message(
                await cache.getBasicCommandCache(key=key)
            )

    @app_commands.command(name="raw")
    async def tagViewRaw(self, interaction: discord.Interaction, name: str):
        """Displays the raw content of a tag

        Args:
            interaction (discord.Interaction): Base interaction
            name (str): Name of the tag
        """
        key = CommandKeyBuilder(id=interaction.guild_id, command="tag display")
        connPool = await memCache.get("main")
        cache = AkariCache(connection_pool=connPool)
        if await cache.cacheExists(key=key) is False:
            tagData = await Tag.prisma().find_first(where={"AND": [{"id": interaction.guild_id}, {"name": {"equals": name}}]})  # type: ignore
            if tagData is None:
                return await interaction.response.send_message(f"{name} was not found")
            await cache.setBasicCommandCache(key=key, value=tagData.content, ttl=30)
            return await interaction.response.send_message(
                escape_markdown(tagData.content)
            )
        else:
            return await interaction.response.send_message(
                await cache.getBasicCommandCache(key=key)
            )

    @app_commands.command(name="create")
    async def tagCreate(self, interaction: discord.Interaction) -> None:
        """Creates a tag

        Args:
            interaction (discord.Interaction): Base interaction
        """
        await interaction.response.send_modal(CreateTag())

    @app_commands.command(name="list")
    async def tagList(self, interaction: discord.Interaction) -> None:
        """Lists all of the tags on the server

        Args:
            interaction (discord.Interaction): Base interaction
        """
        key = CommandKeyBuilder(id=interaction.guild_id, command="tag display")
        connPool = await memCache.get("main")
        cache = AkariCache(connection_pool=connPool)
        if await cache.cacheExists(key=key) is False:
            tagData = await Guild.prisma().find_first(where={"id": interaction.guild_id}, include={"tags": True})  # type: ignore
            if tagData is None:
                return await interaction.response.send_message("No tags were found")
            tagNames = ", ".join([item.name for item in tagData.tags]).rstrip(",")  # type: ignore
            await cache.setBasicCommandCache(key=key, value=tagNames, ttl=5)
            return await interaction.response.send_message(
                embed=discord.Embed(title="Tags", description=tagNames)
            )
        else:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Tags", description=await cache.getBasicCommandCache(key=key)
                )
            )

    @app_commands.command(name="search")
    async def tagSearch(self, interaction: discord.Interaction, name: str) -> None:
        """Search for a tag

        Args:
            interaction (discord.Interaction): _description_
            name (str): Name of the tag
        """
        key = CommandKeyBuilder(id=interaction.guild_id, command="tag display")
        connPool = await memCache.get("main")
        cache = AkariCache(connection_pool=connPool)
        if await cache.cacheExists(key=key) is False:
            data = await Guild.prisma().find_first(where={"AND": [{"id": interaction.guild_id}, {"tags": {"every": {"name": {"contains": name}}}}]}, include={"tags": True})  # type: ignore
            if data is None:
                return await interaction.response.send_message(
                    f"The tag ({name}) does not exist on the server"
                )
            tagNames = "\n".join([f"{i + 1}. {item.name}" for i, item in enumerate(data.tags)])  # type: ignore
            await cache.setBasicCommandCache(key=key, value=tagNames, ttl=5)
            return await interaction.response.send_message(
                embed=discord.Embed(title="Tags", description=tagNames)
            )
        else:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Tags", description=await cache.getBasicCommandCache(key=key)
                )
            )

    @app_commands.command(name="edit")
    async def tagDelete(self, interaction: discord.Interaction) -> None:
        """Edits a tag

        Args:
            interaction (discord.Interaction): Base interaction
        """
        await interaction.response.send_modal(EditTag())


async def setup(bot):
    await bot.add_cog(Tags(bot))
