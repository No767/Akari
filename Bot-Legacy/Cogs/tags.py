import asyncio
import os
import sys
import urllib.parse
from pathlib import Path

import discord
import uvloop
from dateutil import parser
from discord.commands import Option, SlashCommandGroup
from discord.ext import commands, pages
from dotenv import load_dotenv
from rin_exceptions import ItemNotFound
from tortoise import Tortoise

path = Path(__file__).parents[1].absolute()
packagePath = os.path.join(str(path), "Libs")
envPath = os.path.join(str(path), ".env")
sys.path.append(packagePath)

load_dotenv()

from akari_cache import AkariCache, commandKeyBuilder
from akari_tags_utils import AkariTags, AkariTagsUtils
from akari_ui_components import (
    CreateTagModal,
    EditTagContentModal,
    EditTagModal,
    PurgeAllTagsView,
    RemoveTagModal,
)

REDIS_HOST = os.getenv("Redis_Host")
REDIS_PORT = os.getenv("Redis_Port")
POSTGRES_USER = os.getenv("Postgres_User")
POSTGRES_PASSWORD = urllib.parse.quote_plus(os.getenv("Postgres_Password"))
POSTGRES_HOST = os.getenv("Postgres_Host")
POSTGRES_PORT = os.getenv("Postgres_Port")
POSTGRES_DB = os.getenv("Postgres_Akari_DB")
CONNECTION_URI = f"asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

tagsUtils = AkariTagsUtils(uri=CONNECTION_URI, models=["akari_tags_utils.models"])
cache = AkariCache(host=REDIS_HOST, port=REDIS_PORT)


class Tags(commands.Cog):
    """Commands for managing tags, and for displaying tags."""

    def __init__(self, bot):
        self.bot = bot
        self.uri = CONNECTION_URI

    tags = SlashCommandGroup("tags", "Commands for managing tags")
    tagsView = tags.create_subgroup("view", "Commands for viewing tags")
    tagsDelete = tags.create_subgroup("delete", "Commands for deleting tags")
    tagsEdit = tags.create_subgroup("edit", "Commands for editing tags")

    @tagsView.command(name="one")
    async def viewTagsOne(self, ctx, *, name: Option(str, "The tag name to view")):
        """View one tag within a server"""
        key = commandKeyBuilder(
            prefix="cache",
            namespace="akari",
            guild_id=ctx.guild.id,
            command=f"{ctx.command.qualified_name}".replace(" ", "-"),
        )
        await Tortoise.init(
            db_url=self.uri, modules={"models": ["akari_tags_utils.models"]}
        )
        data = (
            await AkariTags.filter(tag_name=name, guild_id=ctx.guild.id)
            .first()
            .values()
        )
        await Tortoise.close_connections()
        try:
            if data is None:
                raise ItemNotFound
            elif await cache.cacheExists(key=key) is True:
                cachedData = await cache.getCommandCache(key=key)
                embed = discord.Embed()
                embed.title = data["tag_name"]
                embed.description = data["tag_content"]
                embed.add_field(
                    name="Created At (UTC)",
                    value=discord.utils.format_dt(
                        parser.isoparse(cachedData["created_at"])
                    ),
                )
                embed.add_field(
                    name="Author",
                    value=self.bot.get_user(cachedData["author_id"]).display_name,
                    inline=True,
                )
                await ctx.respond(embed=embed)
            else:
                await cache.setCommandCache(key=key, value=data, ttl=60)
                embed = discord.Embed()
                embed.title = data["tag_name"]
                embed.description = data["tag_content"]
                embed.add_field(
                    name="Created At (UTC)",
                    value=discord.utils.format_dt(data["created_at"]),
                )
                embed.add_field(
                    name="Author",
                    value=self.bot.get_user(data["author_id"]).display_name,
                    inline=True,
                )
                await ctx.respond(embed=embed)
        except ItemNotFound:
            await ctx.respond(
                embed=discord.Embed(
                    description=f"Sorry, the tag requested ({name}) can't be found. Please try again."
                )
            )

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    @tagsView.command(name="all")
    async def viewTagsOne(self, ctx):
        """Views all tag within a server"""
        data = await tagsUtils.getAllData(guild_id=ctx.guild.id)
        key = commandKeyBuilder(
            prefix="cache",
            namespace="akari",
            guild_id=ctx.guild.id,
            command=f"{ctx.command.qualified_name}".replace(" ", "-"),
        )
        if await cache.cacheExists(key=key) is False:
            try:
                if len(data) == 0:
                    raise ItemNotFound
                else:
                    await cache.setCommandCache(key=key, value=data, ttl=60)
                    mainPages = pages.Paginator(
                        pages=[
                            discord.Embed(
                                title=item["tag_name"], description=item["tag_content"]
                            )
                            .add_field(
                                name="Created At (UTC)",
                                value=discord.utils.format_dt(item["created_at"]),
                            )
                            .add_field(
                                name="Tag Creator",
                                value=item["author_name"],
                            )
                            for item in data
                        ],
                        loop_pages=True,
                    )
                    await mainPages.respond(ctx.interaction, ephemeral=False)
            except ItemNotFound:
                await ctx.respond(
                    embed=discord.Embed(
                        description="It seems like you don't have any tags set up. Please create one to begin!"
                    )
                )
        else:
            cachedData = await cache.getCommandCache(key=key)
            cachedMainPages = pages.Paginator(
                pages=[
                    discord.Embed(
                        title=item["tag_name"], description=item["tag_content"]
                    )
                    .add_field(
                        name="Created At (UTC)",
                        value=discord.utils.format_dt(
                            parser.isoparse(item["created_at"])
                        ),
                    )
                    .add_field(
                        name="Tag Creator",
                        value=item["author_name"],
                    )
                    for item in cachedData
                ],
                loop_pages=True,
            )
            await cachedMainPages.respond(ctx.interaction, ephemeral=False)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    @tagsDelete.command(name="one")
    async def deleteOneTag(self, ctx):
        """Deletes one tag within a server"""
        mainModal = RemoveTagModal(
            uri=self.uri, models=["akari_tags_utils.models"], title="Tag Removal"
        )
        await ctx.send_modal(mainModal)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    @tagsDelete.command(name="all")
    async def deleteAllTags(self, ctx):
        """Deletes all of the tags from the server"""
        embed = discord.Embed()
        embed.description = "Are you sure you want to delete all of the tags from this server? This cannot be undone."
        await ctx.respond(
            embed=embed,
            view=PurgeAllTagsView(
                uri=CONNECTION_URI, models=["akari_tags_utils.models"]
            ),
            ephemeral=True,
        )

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    @tags.command(name="create")
    async def createTag(self, ctx):
        """Creates a tag"""
        modal = CreateTagModal(
            uri=self.uri, models=["akari_tags_utils.models"], title="Tag Creation"
        )
        await ctx.send_modal(modal)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    @tagsEdit.command(name="name")
    async def editTag(self, ctx):
        """Edits the tag's name"""
        mainModal = EditTagModal(
            uri=self.uri, models=["akari_tags_utils.models"], title="Tag Name Edit"
        )
        await ctx.send_modal(mainModal)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    @tagsEdit.command(name="content")
    async def editTagContent(self, ctx):
        """Edits the tag's content"""
        mainModal = EditTagContentModal(
            uri=self.uri, models=["akari_tags_utils.models"], title="Tag Content Edit"
        )
        await ctx.send_modal(mainModal)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    @tags.command(name="display")
    async def displayTag(
        self,
        ctx: discord.ApplicationContext,
        *,
        name: Option(str, "The tag name to display"),
    ):
        """Displays the contents of a tag"""
        key = commandKeyBuilder(
            prefix="cache",
            namespace="akari",
            guild_id=ctx.guild.id,
            command=f"{ctx.command.qualified_name}".replace(" ", "-"),
        )
        await Tortoise.init(
            db_url=self.uri, modules={"models": ["akari_tags_utils.models"]}
        )
        data = (
            await AkariTags.filter(tag_name=name, guild_id=ctx.guild.id)
            .first()
            .values()
        )
        await Tortoise.close_connections()
        try:
            if data is None:
                raise ItemNotFound
            elif await cache.cacheExists(key=key) is True:
                cachedData = await cache.getCommandCache(key=key)
                await ctx.respond(cachedData)
            else:
                await cache.setCommandCache(
                    key=key, value=str(data["tag_content"]), ttl=60
                )
                await ctx.respond(data["tag_content"])
        except ItemNotFound:
            await ctx.respond(
                embed=discord.Embed(
                    description=f"Sorry, the tag requested ({name}) can't be found. Please try again."
                ),
                ephemeral=True,
            )

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    @tags.command(name="raw")
    async def displayRawTag(self, ctx, *, name: Option(str, "The tag name to display")):
        """Displays the contents of a tag raw, with escaped characters"""
        key = commandKeyBuilder(
            prefix="cache",
            namespace="akari",
            guild_id=ctx.guild.id,
            command=f"{ctx.command.qualified_name}".replace(" ", "-"),
        )
        await Tortoise.init(
            db_url=self.uri, modules={"models": ["akari_tags_utils.models"]}
        )
        data = (
            await AkariTags.filter(tag_name=name, guild_id=ctx.guild.id)
            .first()
            .values()
        )
        await Tortoise.close_connections()
        try:
            if data is None:
                raise ItemNotFound
            elif await cache.cacheExists(key=key) is True:
                cachedData = await cache.setCommandCache(
                    key=key, value=str(data["tag_content"]), ttl=60
                )
                await ctx.respond(
                    discord.utils.escape_markdown(text=cachedData["tag_content"])
                )
            else:
                await cache.setCommandCache(
                    key=key, value=str(data["tag_content"]), ttl=60
                )
                await ctx.respond(
                    discord.utils.escape_markdown(text=data["tag_content"])
                )
        except ItemNotFound:
            await ctx.respond(
                embed=discord.Embed(
                    description=f"Sorry, the tag requested ({name}) can't be found. Please try again."
                ),
                ephemeral=True,
            )

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    @tags.command(name="claim")
    async def claimTag(self, ctx, *, name: Option(str, "The tag name to claim")):
        """Allows you to claim a tag"""
        await Tortoise.init(
            db_url=self.uri, modules={"models": ["akari_tags_utils.models"]}
        )
        data = (
            await AkariTags.filter(tag_name=name, guild_id=ctx.guild.id)
            .first()
            .values()
        )
        await Tortoise.close_connections()
        try:
            if data is None:
                raise ItemNotFound
            elif name == ctx.author.name:
                await ctx.respond("You can't claim a tag with your own name.")
            else:
                await AkariTags.filter(tag_name=name, guild_id=ctx.guild.id).update(
                    author_id=ctx.author.id, author_name=ctx.author.name
                )
                await ctx.respond("Successfully claimed the tag!")
        except ItemNotFound:
            await ctx.respond(
                embed=discord.Embed(
                    description=f"Sorry, the tag requested ({name}) can't be found. Please try again."
                ),
                ephemeral=True,
            )

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    @tags.command(name="transfer")
    async def transferAuthorTag(
        self,
        ctx,
        *,
        name: Option(str, "The tag to search for"),
        user: Option(discord.Member, "The new member to transfer the tag's author to"),
    ):
        """Transfers the owner of a tag to another one"""
        await Tortoise.init(
            db_url=self.uri, modules={"models": ["akari_tags_utils.models"]}
        )
        data = (
            await AkariTags.filter(tag_name=name, guild_id=ctx.guild.id)
            .first()
            .values()
        )
        await Tortoise.close_connections()
        try:
            if data is None:
                raise ItemNotFound
            elif user.id == ctx.author.id:
                await ctx.respond("You can't transfer a tag that is yours to yourself.")
            else:
                await AkariTags.filter(tag_name=name, guild_id=ctx.guild.id).update(
                    author_id=user.id, author_name=user.name
                )
                await ctx.respond(f"Successfully transferred the tag to {user.name}!")
        except ItemNotFound:
            await ctx.respond(
                embed=discord.Embed(
                    description=f"Sorry, the tag requested ({name}) can't be found. Please try again."
                ),
                ephemeral=True,
            )

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def setup(bot):
    bot.add_cog(Tags(bot))
