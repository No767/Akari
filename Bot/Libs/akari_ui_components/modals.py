import asyncio
import uuid

import discord
import uvloop
from akari_tags_utils import AkariTags, AkariTagsUtils
from discord.utils import utcnow
from tortoise import Tortoise


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


class CreateTagModal(discord.ui.Modal):
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
                placeholder="Type in the tag name to add",
            )
        )
        self.add_item(
            discord.ui.InputText(
                label="Tag Content",
                style=discord.InputTextStyle.long,
                min_length=1,
                required=True,
                placeholder="Type in the tag content to add",
            )
        )

    async def callback(self, interaction: discord.Interaction):
        if await self.tagsUtils.doesTagExists(
            name=self.children[0].value, guild_id=interaction.guild.id
        ):
            await interaction.response.send_message(
                f"The tag {self.children[0].value} already exists. Please try again",
                ephemeral=True,
            )
        else:
            await self.tagsUtils.createData(
                uuid=str(uuid.uuid4()),
                tag_name=self.children[0].value,
                tag_content=self.children[1].value,
                created_at=utcnow(),
                guild_id=interaction.guild.id,
                author_id=interaction.user.id,
                author_name=interaction.user.name,
            )
            await interaction.response.send_message(
                f"The tag {self.children[0].value} has been created.", ephemeral=True
            )

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class EditTagModal(discord.ui.Modal):
    def __init__(self, uri: str, models: list, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.uri = uri
        self.models = models
        self.tagsUtils = AkariTagsUtils(uri=self.uri, models=self.models)
        self.add_item(
            discord.ui.InputText(
                label="Original Tag Name To Search",
                style=discord.InputTextStyle.short,
                min_length=1,
                required=True,
                placeholder="Type in the original tag name to search for",
            )
        )
        self.add_item(
            discord.ui.InputText(
                label="New Tag Name",
                style=discord.InputTextStyle.short,
                min_length=1,
                required=True,
                placeholder="Type in the new tag name",
            )
        )

    async def callback(self, interaction: discord.Interaction):
        doesTagExist = await self.tagsUtils.doesTagExists(
            name=self.children[0].value, guild_id=interaction.guild.id
        )
        await Tortoise.init(db_url=self.uri, modules={"models": self.models})
        if doesTagExist:
            await AkariTags.filter(
                tag_name=self.children[0].value, guild_id=interaction.guild.id
            ).update(tag_name=self.children[1].value)
            await Tortoise.close_connections()
            await interaction.response.send_message(
                f"The tag {self.children[0].value} has been renamed to {self.children[1].value}",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                f"The tag {self.children[0].value} might have been created yet or cannot be found. If so, either create a new tag first or try again",
                ephemeral=True,
            )

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class EditTagContentModal(discord.ui.Modal):
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
                placeholder="Type in the tag name to search for",
            )
        )
        self.add_item(
            discord.ui.InputText(
                label="New Content",
                style=discord.InputTextStyle.short,
                min_length=1,
                required=True,
                placeholder="Type in the new content",
            )
        )

    async def callback(self, interaction: discord.Interaction):
        doesTagExist = await self.tagsUtils.doesTagExists(
            name=self.children[0].value, guild_id=interaction.guild.id
        )
        await Tortoise.init(db_url=self.uri, modules={"models": self.models})
        if doesTagExist:
            await AkariTags.filter(
                tag_name=self.children[0].value, guild_id=interaction.guild.id
            ).update(tag_content=self.children[1].value)
            await Tortoise.close_connections()
            await interaction.response.send_message(
                f"The tag {self.children[0].value} has been edited", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"The tag {self.children[0].value} might have been created yet or cannot be found. If so, either create a new tag first or try again",
                ephemeral=True,
            )

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
