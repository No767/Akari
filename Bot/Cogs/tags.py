from typing import Any, Dict, List, Optional, Union

import asyncpg
import discord
from akaricore import AkariCore
from discord import app_commands
from discord.ext import commands
from discord.utils import escape_markdown
from Libs.cache import akariCPM, cache, cacheJson
from Libs.ui.tags import CreateTag, DeleteTag, EditTag
from Libs.utils import Embed, encodeDatetime, parseDatetime


class Tags(commands.GroupCog, name="tags"):
    """Akari's custom tags feature, based off of RDanny"""

    def __init__(self, bot: AkariCore) -> None:
        self.bot = bot
        self.pool = self.bot.pool
        self.redis_pool = self.bot.redis_pool
        super().__init__()

    @cacheJson(
        connection_pool=self.redis_pool,
    )
    async def getGuildTag(
        self, id: int, tag_name: str, pool: asyncpg.Pool
    ) -> Union[dict, None]:
        """Gets a tag from the database. This is the JSON model that will be cached

        Args:
            id (int): Guild ID
            tag_name (str): Tag name
            pool (asyncpg.Pool): Asyncpg Connection Pool to pull conns from

        Returns:
            Union[Dict, None]: The tag content or None if it doesn't exist
        """
        sqlQuery = """
        SELECT DISTINCT ON (g.id)
            t.id, t.author_id, t.name, t.aliases, t.created_at
        FROM guild g
        INNER JOIN tag t ON g.id = t.guild_id
        WHERE g.id=$1 AND t.name=$2 OR aliases @> $3;
        """
        async with pool.acquire() as conn:
            res = await conn.fetchrow(sqlQuery, id, tag_name, [tag_name])
            if res is None:
                return None
            return encodeDatetime(dict(res))

    @cache(
        connection_pool=akariCPM.getConnPool(),
    )
    async def getGuildTagText(
        self, id: int, tag_name: str, pool: asyncpg.Pool
    ) -> Union[str, None]:
        """Gets a tag from the database. This is the raw text that will be cached

        Args:
            id (int): Guild ID
            tag_name (str): Tag name

        Returns:
            Union[str, None]: The tag content or None if it doesn't exist
        """
        sqlQuery = """
        SELECT DISTINCT ON (g.id)
            t.content
        FROM guild g
        INNER JOIN tag t ON g.id = t.guild_id
        WHERE g.id=$1 AND t.name=$2 OR aliases @> $3;
        """
        async with pool.acquire() as conn:
            res = await conn.fetchval(sqlQuery, id, tag_name, [tag_name])
            if res is None:
                return None
            return res

    @cacheJson(connection_pool=akariCPM.getConnPool(), ttl=120)
    async def listGuildTags(self, id: int, pool: asyncpg.Pool) -> List[Dict[str, Any]]:
        """Returns a list of all of the tags that the guild owns

        Args:
            id (int): Guild ID
            pool (asyncpg.Pool): Asyncpg connection pool

        Returns:
            List[Dict[str, Any]]: A list of all of the tags that the guild owns
        """
        query = """
        SELECT t.id, t.author_id, t.name, t.aliases, t.content, t.created_at
        FROM guild g
        INNER JOIN tag t ON g.id = t.guild_id
        WHERE g.id=$1;
        """
        async with pool.acquire() as conn:
            res = await conn.fetch(query, id)
            return [encodeDatetime(dict(row)) for row in res]

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
        tagContent = await self.getGuildTagText(interaction.guild.id, name, self.pool)  # type: ignore
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
        tagInfo: dict = await self.getGuildTag(interaction.guild.id, name, self.pool)  # type: ignore
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
