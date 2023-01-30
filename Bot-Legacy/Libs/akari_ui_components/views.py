import asyncio

import discord
import uvloop
from akari_admin_logs import AkariAdminLogsUtils
from akari_cache import AkariCache, commandKeyBuilder
from akari_modmail import AkariModMailConfig
from akari_servers import AkariServers
from akari_tags_utils import AkariTagsUtils
from akari_utils import AkariCM

from .selects import RolesChannelSelect, SetupModMailChannelsSelect


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


class PurgeALDataView(discord.ui.View):
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True

    def __init__(self, uri: str, models: list, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.uri = uri
        self.models = models
        self.alUtils = AkariAdminLogsUtils(uri=self.uri, models=self.models)

    @discord.ui.button(
        label="Yes",
        row=0,
        style=discord.ButtonStyle.primary,
        emoji=discord.PartialEmoji.from_str("<:check:314349398811475968>"),
    )
    async def yes_button_callback(self, button, interaction: discord.Interaction):
        await self.alUtils.purgeAllALData(guild_id=interaction.guild.id)
        await interaction.response.send_message(
            "All of the admin logs have been purged.", ephemeral=True
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


class InitConfirmModMailSetupView(discord.ui.View):
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True

    def __init__(
        self,
        uri: str,
        models: list,
        redis_host: str,
        redis_port: int,
        command_name: str,
        guild: discord.Guild,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.uri = uri
        self.models = models
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.command_name = command_name
        self.guild = guild
        self.cache = AkariCache(host=self.redis_host, port=self.redis_port)
        self.add_item(
            SetupModMailChannelsSelect(
                redis_host=self.redis_host,
                redis_port=self.redis_port,
                command_name=self.command_name,
                guild=self.guild,
            )
        )

    @discord.ui.button(
        label="Confirm",
        row=1,
        style=discord.ButtonStyle.primary,
        emoji=discord.PartialEmoji.from_str("<:check:314349398811475968>"),
    )
    async def yes_button_callback(self, button, interaction: discord.Interaction):
        key = commandKeyBuilder(
            prefix="cache",
            namespace="akari",
            guild_id=interaction.guild.id,
            command=f"{self.command_name}-channel".replace(" ", "-"),
        )
        channelModMail = await self.cache.getCommandCacheDict(key=key)
        async with AkariCM(uri=self.uri, models=self.models):
            serverConf = (
                await AkariServers.filter(guild_id=interaction.guild.id)
                .first()
                .values()
            )
            if serverConf["modmail"] is False:
                await AkariServers.filter(guild_id=interaction.guild.id).update(
                    modmail=True
                )
            elif (
                await AkariModMailConfig.filter(guild_id=interaction.guild.id).exists()
                is False
            ):
                await AkariModMailConfig(
                    guild_id=interaction.guild.id,
                    channel_name=channelModMail["channel_name"],
                    channel_id=int(channelModMail["channel_id"]),
                ).save()
            else:
                await AkariModMailConfig.filter(guild_id=interaction.guild.id).update(
                    channel_name=channelModMail["channel_name"],
                    channel_id=int(channelModMail["channel_id"]),
                )
            await interaction.response.send_message(
                "ModMail has been successfully enabled!",
                ephemeral=True,
            )

    @discord.ui.button(
        label="Cancel",
        row=1,
        style=discord.ButtonStyle.primary,
        emoji=discord.PartialEmoji.from_str("<:xmark:314349398824058880>"),
    )
    async def no_button_callback(self, button, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"The operation has been canceled by the user {interaction.user.name}",
            ephemeral=True,
        )


class InitConfirmRolesSetupView(discord.ui.View):
    def __init__(
        self,
        uri: str,
        models: list,
        redis_host: str,
        redis_port: int,
        command_name: str,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.uri = uri
        self.models = models
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.command_name = command_name
        self.cache = AkariCache(host=self.redis_host, port=self.redis_port)
        self.add_item(
            RolesChannelSelect(
                redis_host=self.redis_host,
                redis_port=self.redis_port,
                command_name=self.command_name,
            )
        )
