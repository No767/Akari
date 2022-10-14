import asyncio

import discord
import uvloop
from akari_tags_utils import AkariTagsUtils


class PurgeAllTagsView(discord.ui.View):
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True

    def __init__(self, uri: str, models: list, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.uri = uri
        self.models = models
        self.tagsUtils = AkariTagsUtils(uri=self.uri, models=self.models)

    @discord.ui.button(
        label="Yes",
        row=0,
        style=discord.ButtonStyle.primary,
        emoji=discord.PartialEmoji.from_str("<:check:314349398811475968>"),
    )
    async def yes_button_callback(self, button, interaction: discord.Interaction):
        await self.tagsUtils.purgeData(guild_id=interaction.guild.id)
        await interaction.response.send_message(
            "All of the tags have been purged.", ephemeral=True
        )

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    @discord.ui.button(
        label="No",
        row=0,
        style=discord.ButtonStyle.primary,
        emoji=discord.PartialEmoji.from_str("<:xmark:314349398824058880>"),
    )
    async def no_button_callback(self, button, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"The operation has been canceled by the user {interaction.user.name}",
            ephemeral=True,
        )

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
