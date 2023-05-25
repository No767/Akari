from typing import Optional

import discord
from akaricore import AkariCore
from discord import app_commands
from discord.ext import commands
from discord.utils import escape_markdown
from Libs.tags import getGuildTag, getGuildTagText
from Libs.utils import Embed
from Libs.ui.tags import EditTag, CreateTag, DeleteTag


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
        tagInfo = await getGuildTag(interaction.guild.id, name, self.pool)  # type: ignore
        if tagInfo is None:
            await interaction.response.send_message("Sorry but the tag was not found")
            return
        embed = Embed()
        embed.title = tagInfo["name"]  # type: ignore
        embed.add_field(name="Owner", value=f"<@{tagInfo['author_id']}>")  # type: ignore
        embed.add_field(name="Aliases", value=tagInfo["aliases"])  # type: ignore
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
        # TODO: Add a check if the tag doesn't exist or not
        deleteTagView = DeleteTag(self.pool, name)
        await interaction.response.send_message(embed=Embed(description=f"Are you sure you want to delete the current tag? {name}"), view=deleteTagView)
        
async def setup(bot: AkariCore) -> None:
    await bot.add_cog(Tags(bot))
