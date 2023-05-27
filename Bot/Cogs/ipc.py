import os
from typing import Any, Dict

from akaricore import AkariCore
from discord.ext import commands
from discord.ext.ipc.objects import ClientPayload
from discord.ext.ipc.server import Server
from dotenv import load_dotenv
from Libs.tags import getGuildTag, getGuildTagText, listGuildTags

load_dotenv()

IPC_SECRET_KEY = os.environ["IPC_SECRET_KEY"]
IPC_HOST = os.environ["IPC_HOST"]


class IPCServer(commands.Cog):
    """Akari's own IPC server"""

    def __init__(self, bot: AkariCore):
        self.bot = bot
        self.pool = self.bot.pool
        self.ipc = Server(self.bot, secret_key=IPC_SECRET_KEY, host=IPC_HOST)

    async def cog_load(self) -> None:
        await self.ipc.start()

    async def cog_unload(self) -> None:
        await self.ipc.stop()

    @Server.route()
    async def get_tag(self, data: ClientPayload) -> Any:
        guildTag = await getGuildTag(
            id=data.guild_id, tag_name=data.tag_name, pool=self.pool
        )
        return guildTag

    @Server.route()
    async def get_tag_content(self, data: ClientPayload) -> Dict:
        guildTagContent = await getGuildTagText(
            id=data.guild_id, tag_name=data.tag_name, pool=self.pool
        )
        return {"data": guildTagContent}

    @Server.route()
    async def get_all_guild_tag(self, data: ClientPayload) -> Dict:
        guildTagList = await listGuildTags(id=data.guild_id, pool=self.pool)
        return {"data": guildTagList}


async def setup(bot: AkariCore) -> None:
    await bot.add_cog(IPCServer(bot))
