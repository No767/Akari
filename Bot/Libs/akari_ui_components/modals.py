import asyncio

import discord
import uvloop
from akari_tags_utils import AkariTagsUtils


class RemoveTagModal(discord.ui.Modal):
    def __init__(self, uri: str, models: list, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.uri = uri
        self.models = models
        self.tagsUtils = AkariTagsUtils(uri=self.uri, models=self.models)
        self.add_item(
            discord.ui.InputText(
                label="Tag Name",
                style=discord.InputTextStyle.short,
                min_length=1,
                required=True,
                placeholder="Type in the tag name to delete",
            )
        )

    async def callback(self, interaction: discord.Interaction):
        if await self.tagsUtils.doesTagExists(
            name=self.children[0].value, guild_id=interaction.guild.id
        ):
            await self.tagsUtils.removeTag(
                name=self.children[0].value, guild_id=interaction.guild_id
            )
            await interaction.response.send_message(
                f"The tag {self.children[0].value} has been removed.", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"The tag {self.children[0].value} doesn't exist. Please try again",
                ephemeral=True,
            )

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
