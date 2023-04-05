import logging
import os

import discord
from akaricore import AkariCore
from anyio import run
from dotenv import load_dotenv

load_dotenv()

AKARI_TOKEN = os.environ["AKARI_DEV_TOKEN"]

intents = discord.Intents.default()
intents.message_content = True

FORMATTER = logging.Formatter(
    fmt="%(asctime)s %(levelname)s    %(message)s", datefmt="[%Y-%m-%d %H:%M:%S]"
)
discord.utils.setup_logging(formatter=FORMATTER)
discord.utils.setup_logging(formatter=FORMATTER)
logger = logging.getLogger("discord")


async def main():
    async with AkariCore(intents=intents, dev_mode=True) as bot:
        await bot.start(AKARI_TOKEN)


if __name__ == "__main__":
    try:
        run(main, backend_options={"use_uvloop": True})
    except KeyboardInterrupt:
        logger.info("Shutting down Akari...")
