from tortoise import Tortoise
import asyncio
import uvloop
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import urllib.parse

path = Path(__file__).parents[0].absolute()
packagePath = os.path.join(str(path), "Lib")
envPath = os.path.join(str(path), "Bot", ".env")
sys.path.append(packagePath)

load_dotenv(envPath)

POSTGRES_USER = os.getenv("Postgres_User")
POSTGRES_PASSWORD = urllib.parse.quote_plus(os.getenv("Postgres_Password"))
POSTGRES_HOST = os.getenv("Postgres_Host")
POSTGRES_PORT = os.getenv("Postgres_Port")
POSTGRES_TAGS_DB = os.getenv("Postgres_Tags_DB")
CONNECTION_URI = f"asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_TAGS_DB}"

async def init():
    await Tortoise.init(
        db_url=CONNECTION_URI,
        modules={'models': ['akari_tags_utils.models']}
    )
    await Tortoise.generate_schemas()
    await Tortoise.close_connections()
    print("[DB Seeder] Generated all schemas for Akari")
    
if __name__ == "__main__":
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    asyncio.run(init())