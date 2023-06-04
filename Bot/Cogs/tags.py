from typing import Optional

import discord
from akaricore import AkariCore
from discord import app_commands
from discord.ext import commands
from discord.utils import escape_markdown
from Libs.tags import getGuildTag, getGuildTagText
from Libs.ui.tags import CreateTag, DeleteTag, EditTag
from Libs.utils import Embed, parseDatetime
from Libs.utils.pages import AkariPages


class Tags(commands.GroupCog, name="tags"):
    """Akari's custom tags feature, based off of RDanny"""

    def __init__(self, bot: AkariCore) -> None:
        self.bot = bot
        self.pool = self.bot.pool
        super().__init__()

    @app_commands.command(name="get")
    async def getTag(
        self, interaction: discord.Interaction, name: str, raw: Optional[bool] = False
    ) -> None:
        """Gets a tag

        Args:
            interaction (discord.Interaction): Base interaction
            name (str): The name of the tag to look for
            raw (Optional[bool]): Whether to display the raw text or not
        """
        tagContent = await getGuildTagText(interaction.guild.id, name, self.pool)  # type: ignore
        if tagContent is None:
            await interaction.response.send_message("Sorry but the tag was not found")
            return
        finalContent = escape_markdown(tagContent) if raw is True else tagContent
        await interaction.response.send_message(finalContent)

    @app_commands.command(name="info")
    async def tagInfo(self, interaction: discord.Interaction, name: str) -> None:
        """Provides with info about an tag

        Args:
            interaction (discord.Interaction): Base interaction
            name (str): Name of tag
        """
        tagInfo: dict = await getGuildTag(interaction.guild.id, name, self.pool)  # type: ignore
        if tagInfo is None:
            await interaction.response.send_message("Sorry but the tag was not found")
            return
        embed = Embed()
        embed.title = tagInfo["name"]
        embed.add_field(name="Owner", value=f"<@{tagInfo['author_id']}>")
        embed.add_field(name="Aliases", value=tagInfo["aliases"])
        embed.set_footer(
            text=f"Created at: {parseDatetime(tagInfo['created_at']).strftime('%A, %d %B %Y %H:%M')}"
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="edit")
    async def editTag(self, interaction: discord.Interaction) -> None:
        """Edits a tag

        Args:
            interaction (discord.Interaction): Base interaction
        """
        editModal = EditTag(self.pool)
        await interaction.response.send_modal(editModal)

    @app_commands.command(name="create")
    async def createTag(self, interaction: discord.Interaction) -> None:
        """Creates a new tag

        Args:
            interaction (discord.Interaction): Base interaction
        """
        createTagModal = CreateTag(self.pool)
        await interaction.response.send_modal(createTagModal)

    @app_commands.command(name="delete")
    async def deleteTag(self, interaction: discord.Interaction, name: str) -> None:
        """Deletes a tag

        Args:
            interaction (discord.Interaction): Base interaction
            name (str): Name of tag
        """
        selectQuery = """
        SELECT DISTINCT (name, aliases) FROM tag WHERE name=$1 OR aliases @> $2;
        """
        async with self.pool.acquire() as conn:
            selCheck = await conn.fetchrow(selectQuery, name, [name])
            if selCheck is None:
                await interaction.response.send_message(
                    "The tag could not be found. Please try again"
                )
                return
            deleteTagView = DeleteTag(self.pool, name)
            await interaction.response.send_message(
                embed=Embed(
                    description=f"Are you sure you want to delete the current tag? {name}"
                ),
                view=deleteTagView,
            )

    @app_commands.command(name="alias")
    async def aliasTag(
        self, interaction: discord.Interaction, name: str, alias: str
    ) -> None:
        """Aliases a tag

        Args:
            interaction (discord.Interaction): Base interaction
            name (str): The original name of the tag
            alias (str): The alias of the tag
        """
        selectQuery = """
        SELECT DISTINCT ON (g.id)
            t.name, t.aliases
        FROM guild g
        INNER JOIN tag t ON g.id = t.guild_id
        WHERE g.id=$1 AND t.name=$2;
        """
        updateQuery = """
        UPDATE tag
        SET aliases=array_append(aliases, $4)
        WHERE tag.guild_id=$1 AND tag.author_id=$2 AND tag.name=$3;
        """
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                res = await conn.fetchrow(selectQuery, interaction.guild.id, name)  # type: ignore
                if res is None:
                    await interaction.response.send_message(
                        "Sorry but the tag was not found"
                    )
                    return
                await conn.execute(updateQuery, interaction.guild.id, interaction.user.id, name, alias)  # type: ignore
                await interaction.response.send_message(
                    f"The tag is now aliased to {alias}"
                )

    @app_commands.command(name="search")
    async def searchTag(self, interaction: discord.Interaction, name: str) -> None:
        # This was written before my flight to Tokyo
        # ! PROBABLY WILL NOT WORK
        """Searches for a tag

        Args:
            interaction (discord.Interaction): Interaction
            name (str): Tag to search
        """
        selectQuery = """
        SELECT DISTINCT ON (g.id)
            t.name, t.aliases
        FROM guild g
        INNER JOIN tag t ON g.id = t.guild_id
        WHERE g.id=$1 AND t.name=$2;
        """
        async with self.pool.acquire() as conn:
            res = await conn.fetch(selectQuery, interaction.guild.id, name)  # type: ignore
            if len(res) == 0:
                await interaction.response.send_message(
                    "Sorry but the tag was not found"
                )
                return
            AkariPages(self.bot, interaction)
            # TODO: Finish the sources later (on flight)


async def setup(bot: AkariCore) -> None:
    await bot.add_cog(Tags(bot))
