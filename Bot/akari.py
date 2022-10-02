import logging
import os
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("Akari_Dev_Token")
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(intents=intents)

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] | %(asctime)s >> %(message)s",
    datefmt="[%m/%d/%Y] [%I:%M:%S %p %Z]",
)

path = Path(__file__).parents[0].absolute()
cogsPath = os.path.join(str(path), "Cogs")

for cogs in os.listdir(cogsPath):
    if cogs.endswith(".py"):
        bot.load_extension(f"Cogs.{cogs[:-3]}", store=False)
        
@bot.event
async def on_ready():
    logging.info("Akari is ready!")
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="/help")
    )

if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)