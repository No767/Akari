import discord
from akaricore import AkariCore
from discord import app_commands
from discord.ext import commands
from Libs.cog_utils.tags import format_options, get_tag_content
from Libs.ui.tags import CreateTagModal, TagPages

# from Libs.ui.tags import CreateTag, DeleteTag, EditTag


class Tags(commands.GroupCog, name="tags"):
    """Akari's custom tags feature, based off of RDanny"""

    def __init__(self, bot: AkariCore) -> None:
        self.bot = bot
        self.pool = self.bot.pool
        self.redis_pool = self.bot.redis_pool
        super().__init__()

    @app_commands.command(name="get")
    @app_commands.describe(name="The name of the tag")
    async def get(self, interaction: discord.Interaction, name: str) -> None:
        """Obtain text for a tag"""
        text = await get_tag_content(interaction.guild.id, name, self.pool)  # type: ignore
        if isinstance(text, list):
            await interaction.response.send_message(format_options(text) or ".")
            return
        await interaction.response.send_message(text or ".")

    @app_commands.command(name="search")
    @app_commands.describe(query="The name to look for")
    async def search(self, interaction: discord.Interaction, query: str) -> None:
        """Search for tags"""
        if len(query) < 3:
            await interaction.response.send_message(
                "The query must be at least 3 characters"
            )
            return

        sql = """SELECT id, name, owner_id
                 FROM tag_lookup
                 WHERE guild_id=$1 AND name % $2
                 ORDER BY similarity(name, $2) DESC
                 LIMIT 100;
              """
        rows = await self.pool.fetch(sql, interaction.guild.id, query)  # type: ignore

        if rows:
            pages = TagPages(entries=rows, per_page=10, interaction=interaction)
            await pages.start()
        else:
            await interaction.response.send_message("No tags found")

    @app_commands.command(name="create")
    async def create(self, interaction: discord.Interaction) -> None:
        """Create a tag"""
        modal = CreateTagModal(self.pool)
        await interaction.response.send_modal(modal)

    # @app_commands.command(name="get")
    # async def getTag(
    #     self, interaction: discord.Interaction, name: str, raw: Optional[bool] = False
    # ) -> None:
    #     """Gets a tag

    #     Args:
    #         interaction (discord.Interaction): Base interaction
    #         name (str): The name of the tag to look for
    #         raw (Optional[bool]): Whether to display the raw text or not
    #     """
    #     tagContent = await getGuildTagText(id=interaction.guild.id, redis_pool=self.redis_pool, tag_name=name, db_pool=self.pool)  # type: ignore
    #     if tagContent is None or isinstance(tagContent, str) is False:
    #         await interaction.response.send_message(formatOptions(tagContent))  # type: ignore
    #         return
    #     finalContent = escape_markdown(tagContent) if raw is True else tagContent  # type: ignore
    #     await interaction.response.send_message(finalContent)

    # @app_commands.command(name="info")
    # async def tagInfo(self, interaction: discord.Interaction, name: str) -> None:
    #     """Provides with info about an tag

    #     Args:
    #         interaction (discord.Interaction): Base interaction
    #         name (str): Name of tag
    #     """
    #     tagInfo: dict = await getGuildTag(id=interaction.guild.id, redis_pool=self.redis_pool, tag_name=name, db_pool=self.pool)  # type: ignore
    #     if tagInfo is None:
    #         await interaction.response.send_message("Sorry but the tag was not found")
    #         return
    #     embed = Embed()
    #     embed.title = tagInfo["name"]
    #     embed.timestamp = utcnow()
    #     embed.add_field(name="Owner", value=f"<@{tagInfo['author_id']}>")
    #     embed.add_field(
    #         name="Created At", value=format_dt(parseDatetime(tagInfo["created_at"]))
    #     )
    #     # embed.add_field(name="Aliases", value=tagInfo["aliases"])
    #     await interaction.response.send_message(embed=embed)

    # @app_commands.command(name="edit")
    # async def editTag(self, interaction: discord.Interaction) -> None:
    #     """Edits a tag

    #     Args:
    #         interaction (discord.Interaction): Base interaction
    #     """
    #     editModal = EditTag(self.pool)
    #     await interaction.response.send_modal(editModal)

    # @app_commands.command(name="create")
    # async def createTag(self, interaction: discord.Interaction) -> None:
    #     """Creates a new tag

    #     Args:
    #         interaction (discord.Interaction): Base interaction
    #     """
    #     createTagModal = CreateTag(self.pool)
    #     await interaction.response.send_modal(createTagModal)

    # @app_commands.command(name="delete")
    # async def deleteTag(self, interaction: discord.Interaction, name: str) -> None:
    #     """Deletes a tag

    #     Args:
    #         interaction (discord.Interaction): Base interaction
    #         name (str): Name of tag
    #     """
    #     selectQuery = """
    #     SELECT DISTINCT (name, aliases) FROM tag WHERE name=$1 OR aliases @> $2;
    #     """
    #     async with self.pool.acquire() as conn:
    #         selCheck = await conn.fetchrow(selectQuery, name, [name])
    #         if selCheck is None:
    #             await interaction.response.send_message(
    #                 "The tag could not be found. Please try again"
    #             )
    #             return
    #         deleteTagView = DeleteTag(self.pool, name)
    #         await interaction.response.send_message(
    #             embed=Embed(
    #                 description=f"Are you sure you want to delete the current tag? {name}"
    #             ),
    #             view=deleteTagView,
    #         )

    # @app_commands.command(name="alias")
    # async def aliasTag(
    #     self, interaction: discord.Interaction, name: str, alias: str
    # ) -> None:
    #     """Aliases a tag

    #     Args:
    #         interaction (discord.Interaction): Base interaction
    #         name (str): The original name of the tag
    #         alias (str): The alias of the tag
    #     """
    #     selectQuery = """
    #     SELECT DISTINCT ON (g.id)
    #         t.name, t.aliases
    #     FROM guild g
    #     INNER JOIN tag t ON g.id = t.guild_id
    #     WHERE g.id=$1 AND t.name=$2;
    #     """
    #     updateQuery = """
    #     UPDATE tag
    #     SET aliases=array_append(aliases, $4)
    #     WHERE tag.guild_id=$1 AND tag.author_id=$2 AND tag.name=$3;
    #     """
    #     async with self.pool.acquire() as conn:
    #         async with conn.transaction():
    #             res = await conn.fetchrow(selectQuery, interaction.guild.id, name)  # type: ignore
    #             if res is None:
    #                 await interaction.response.send_message(
    #                     "Sorry but the tag was not found"
    #                 )
    #                 return
    #             await conn.execute(updateQuery, interaction.guild.id, interaction.user.id, name, alias)  # type: ignore
    #             await interaction.response.send_message(
    #                 f"The tag is now aliased to {alias}"
    #             )

    # @app_commands.command(name="search")
    # async def searchTag(self, interaction: discord.Interaction, name: str) -> None:
    #     # This was written before my flight to Tokyo
    #     # ! PROBABLY WILL NOT WORK
    #     """Searches for a tag

    #     Args:
    #         interaction (discord.Interaction): Interaction
    #         name (str): Tag to search
    #     """
    #     selectQuery = """
    #     SELECT DISTINCT ON (g.id)
    #         t.name, t.aliases
    #     FROM guild g
    #     INNER JOIN tag t ON g.id = t.guild_id
    #     WHERE g.id=$1 AND t.name=$2;
    #     """
    #     async with self.pool.acquire() as conn:
    #         res = await conn.fetch(selectQuery, interaction.guild.id, name)  # type: ignore
    #         if len(res) == 0:
    #             await interaction.response.send_message(
    #                 "Sorry but the tag was not found"
    #             )
    #             return
    #         AkariPages(self.bot, interaction)
    #         # TODO: Finish the sources later (on flight)

    # TODO: Add checks since only the owner can do this
    # @app_commands.command(name="export")
    # async def exportTags(self, interaction: discord.Interaction) -> None:
    #     """Exports all of the tags that the guild has as an JSON document

    #     Args:
    #         interaction (discord.Interaction): _description_
    #     """


async def setup(bot: AkariCore) -> None:
    await bot.add_cog(Tags(bot))
