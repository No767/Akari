import asyncio
import logging
import os
import urllib.parse

import discord
import uvloop
from akaricore import AkariCore
from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER = os.getenv("Postgres_User")
POSTGRES_PASSWORD = urllib.parse.quote_plus(os.getenv("Postgres_Password"))
POSTGRES_HOST = os.getenv("Postgres_Host")
POSTGRES_PORT = os.getenv("Postgres_Port")
POSTGRES_DB = os.getenv("Postgres_Akari_DB")
CONNECTION_URI = f"asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
MODELS = [
    "akari_tags_utils.models",
    "akari_admin_logs.models",
    "akari_servers.models",
    "akari_modmail.models",
]

DISCORD_BOT_TOKEN = os.getenv("Akari_Dev_Token")
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
bot = AkariCore(uri=CONNECTION_URI, models=MODELS, intents=intents)

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] | %(asctime)s >> %(message)s",
    datefmt="[%m/%d/%Y] [%I:%M:%S %p %Z]",
)

if __name__ == "__main__":
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    bot.run(DISCORD_BOT_TOKEN)
