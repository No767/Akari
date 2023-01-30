import logging
import os

import discord
from akaricore import AkariCore
from anyio import run
from dotenv import load_dotenv
from rich.logging import RichHandler

load_dotenv()

DEV_GUILD = discord.Object(id=970159505390325842)
AKARI_TOKEN = os.environ["AKARI_DEV_TOKEN"]
intents = discord.Intents.default()
intents.message_content = True

FORMATTER = logging.Formatter(fmt="%(message)s", datefmt="[%Y-%m-%d %H:%M:%S]")
HANDLER = RichHandler(show_path=False)
discord.utils.setup_logging(handler=HANDLER, formatter=FORMATTER)
logger = logging.getLogger("discord")


async def main():
    async with AkariCore(intents=intents, testing_guild_id=DEV_GUILD.id) as bot:
        await bot.start(AKARI_TOKEN)


if __name__ == "__main__":
    try:
        run(main, backend_options={"use_uvloop": True})
    except KeyboardInterrupt:
        logger.info("Shutting down Akari...")
