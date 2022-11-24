import asyncio
import logging
import os

import discord
import uvloop
from akaricore import AkariCore
from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("Akari_Dev_Token")
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
bot = AkariCore(intents=intents)

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] | %(asctime)s >> %(message)s",
    datefmt="[%m/%d/%Y] [%I:%M:%S %p %Z]",
)
logging.getLogger("tortoise").setLevel(logging.WARNING)

if __name__ == "__main__":
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    bot.run(DISCORD_BOT_TOKEN)
