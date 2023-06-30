import os

import asyncpg
import discord
from aiohttp import ClientSession
from akaricore import AkariCore
from anyio import run
from dotenv import load_dotenv
from Libs.cache import AkariCPM
from Libs.utils import AkariLogger

load_dotenv()

AKARI_TOKEN = os.environ["AKARI_DEV_TOKEN"]
POSTGRES_URI = os.environ["POSTGRES_URI"]
REDIS_URI = os.environ["REDIS_URI"]

intents = discord.Intents.default()
intents.message_content = True


async def main():
    async with ClientSession() as session, asyncpg.create_pool(
        dsn=POSTGRES_URI, command_timeout=60, max_size=20, min_size=20
    ) as pool, AkariCPM(uri=REDIS_URI) as redis_pool:
        async with AkariCore(
            intents=intents,
            session=session,
            pool=pool,
            redis_pool=redis_pool,
            dev_mode=True,
        ) as bot:
            await bot.start(AKARI_TOKEN)


if __name__ == "__main__":
    try:
        with AkariLogger():
            run(main, backend_options={"use_uvloop": True})
    except KeyboardInterrupt:
        pass
