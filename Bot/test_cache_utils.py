import asyncio
import os

import asyncpg
from dotenv import load_dotenv
from Libs.tags import getGuildTagText
from redis.asyncio.connection import ConnectionPool

load_dotenv()

POSTGRES_URI = os.getenv("POSTGRES_URI")


async def main():
    async with asyncpg.create_pool(dsn=POSTGRES_URI, min_size=20, max_size=20) as pool:
        res = await getGuildTagText(
            970159505390325842,
            ConnectionPool.from_url("redis://localhost:6379/0"),
            "uwl",
            pool,
        )
        print(res)


asyncio.run(main())
