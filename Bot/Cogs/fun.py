import asyncio
import random

import aiohttp
import discord
import orjson
import simdjson
import uvloop
from discord.commands import Option, SlashCommandGroup
from discord.ext import commands, pages
from rin_exceptions import NoItemsError

parser = simdjson.Parser()


class Fun(commands.Cog):
    """Fun commands to mess around with"""

    def __init__(self, bot):
        self.bot = bot

    fun = SlashCommandGroup(
        "fun",
        "Commands for messing around with the bot",
    )

    @fun.command(name="memes")
    async def getMemes(
        self,
        ctx,
        *,
        subreddit: Option(str, "The subreddit to search", required=False),
        amount: Option(
            int,
            "How much memes do you want returned?",
            min_value=1,
            max_value=50,
            default=10,
        ),
    ):
        """Get some spicy memes from Reddit"""
        sub = subreddit
        if sub is None:
            subList = ["memes", "dankmemes", "me_irl"]
            sub = random.choice(subList)  # nosec
        elif "r/" in sub:
            subSplit = sub.split("/")
            sub = subSplit[1]
        async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
            async with session.get(
                f"https://meme-api.herokuapp.com/gimme/{sub}/{amount}"
            ) as r:
                data = await r.content.read()
                dataMain = parser.parse(data, recursive=True)
                try:
                    if len(dataMain["memes"]) == 0 or r.status == 404:
                        raise NoItemsError
                    else:
                        mainPages = pages.Paginator(
                            pages=[
                                discord.Embed(title=items["title"])
                                .add_field(
                                    name="Author", value=items["author"], inline=True
                                )
                                .add_field(
                                    name="Subreddit",
                                    value=items["subreddit"],
                                    inline=True,
                                )
                                .add_field(
                                    name="Upvotes", value=items["ups"], inline=True
                                )
                                .add_field(
                                    name="NSFW", value=items["nsfw"], inline=True
                                )
                                .add_field(
                                    name="Spoiler", value=items["spoiler"], inline=True
                                )
                                .add_field(
                                    name="Reddit URL",
                                    value=items["postLink"],
                                    inline=True,
                                )
                                .set_image(url=items["url"])
                                for items in dataMain["memes"]
                            ],
                            loop_pages=True,
                        )
                        await mainPages.respond(ctx.interaction, ephemeral=False)
                except NoItemsError:
                    embedError = discord.Embed()
                    embedError.description = "Sorry, but there are no memes to be found within that subreddit. Please try again."
                    await ctx.respond(embedError)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    @fun.command(name="coinflip")
    async def coinFlip(self, ctx):
        """Flips a coin"""
        coinList = ["Heads", "Tails"]
        coinFlip = random.choice(coinList)  # nosec
        await ctx.respond(f"The coin landed on {coinFlip.lower()}")

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    @fun.command(name="diceroll")
    async def diceRoll(
        self,
        ctx,
        *,
        sides: Option(
            int,
            "How much sides does that die have",
            min_value=1,
            max_value=100,
            default=6,
        ),
    ):
        """Rolls a die"""
        roll = random.randint(1, sides)  # nosec
        await ctx.respond(f"The die landed on a {roll}")

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def setup(bot):
    bot.add_cog(Fun(bot))
