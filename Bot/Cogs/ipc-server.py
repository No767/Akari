import os
from typing import Dict

from discord.ext import commands
from discord.ext.ipc.objects import ClientPayload
from discord.ext.ipc.server import Server
from dotenv import load_dotenv
from prisma.models import Guild, Tag  # type: ignore

load_dotenv()

IPC_SECRET_KEY = os.environ["IPC_SECRET_KEY"]
IPC_HOST = os.environ["IPC_HOST"]


class IPCServer(commands.Cog):
    """Akari's own IPC server"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ipc = Server(self.bot, secret_key=IPC_SECRET_KEY, host=IPC_HOST)

    async def cog_load(self) -> None:
        await self.ipc.start()

    async def cog_unload(self) -> None:
        await self.ipc.stop()

    @Server.route()
    async def get_user_data(self, data: ClientPayload) -> Dict:
        user = await self.bot.fetch_user(data.user_id)
        return user._to_minimal_user_json()

    @Server.route()
    async def create_tag(self, data: ClientPayload) -> None:
        await Guild.prisma().update(
            where={"id": data.guild_id},
            data={"tags": {"create": [{"name": data.name, "content": data.content}]}},
        )

    @Server.route()
    async def get_tag(self, data: ClientPayload) -> Dict:
        tagRes = await Guild.prisma().find_first(
            where={
                "id": data.guild_id,
                "tags": {"every": {"name": {"contains": data.name}}},
            }
        )
        if tagRes is None:
            return {"message": "Tag not found"}
        return tagRes.dict()


async def setup(bot):
    await bot.add_cog(IPCServer(bot))
