import os
from typing import Dict

from discord.ext import commands
from discord.ext.ipc.objects import ClientPayload
from discord.ext.ipc.server import Server
from dotenv import load_dotenv

load_dotenv()

IPC_SECRET_KEY = os.environ["IPC_SECRET_KEY"]


class IPCServer(commands.Cog):
    """Akari's own IPC server"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ipc = Server(self.bot, secret_key=IPC_SECRET_KEY)

    async def cog_load(self) -> None:
        await self.ipc.start()

    async def cog_unload(self) -> None:
        await self.ipc.stop()

    @Server.route()
    async def get_user_data(self, data: ClientPayload) -> Dict:
        user = await self.bot.fetch_user(data.user_id)
        return user._to_minimal_user_json()


async def setup(bot):
    await bot.add_cog(IPCServer(bot))
