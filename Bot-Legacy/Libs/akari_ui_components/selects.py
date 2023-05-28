import discord
from akari_cache import AkariCache, commandKeyBuilder


class SetupModMailChannelsSelect(discord.ui.Select):
    def __init__(
        self, redis_host: str, redis_port: int, command_name: str, guild: discord.Guild
    ):
        super().__init__(
            select_type=discord.ComponentType.channel_select,
            placeholder="Choose what channel will ModMail reports be sent to",
            min_values=1,
            max_values=1,
            channel_types=[discord.ChannelType.text],
            row=0,
        )
        self.command_name = command_name
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.cache = AkariCache(host=self.redis_host, port=self.redis_port)

    async def callback(self, interaction: discord.Interaction):
        key = commandKeyBuilder(
            prefix="cache",
            namespace="akari",
            guild_id=interaction.guild.id,
            command=f"{self.command_name}-channel".replace(" ", "-"),
        )
        await self.cache.setCommandCacheDict(
            key=key,
            value={
                "channel_name": self.values[0].name,
                "channel_id": str(self.values[0].id),
            },
            ttl=180,
        )  # 180 seconds is the default timeout for views
        await interaction.response.send_message(
            f"The channel where Akari's ModMail will publish is: {self.values[0].mention}",
            ephemeral=True,
        )


class RolesChannelSelect(discord.ui.Select):
    def __init__(self, redis_host: str, redis_port: int, command_name: str):
        super().__init__(
            select_type=discord.ComponentType.channel_select,
            placeholder="Choose what channels the dropdown roles will be selected to",
            min_values=1,
            max_values=1,
            channel_types=[discord.ChannelType.text],
            row=0,
        )
        self.command_name = command_name
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.cache = AkariCache(host=self.redis_host, port=self.redis_port)

    async def callback(self, interaction: discord.Interaction):
        key = commandKeyBuilder(
            prefix="cache",
            namespace="akari",
            guild_id=interaction.guild.id,
            command=f"{self.command_name}-channel".replace(" ", "-"),
        )
        await self.cache.setCommandCacheDict(
            key=key,
            value={
                "channel_name": self.values[0].name,
                "channel_id": str(self.values[0].id),
            },
            ttl=180,
        )  # 180 seconds is the default timeout for views
        await interaction.response.send_message(
            f"The selected channel where roles will be sent is: {self.values[0].mention}",
            ephemeral=True,
        )
