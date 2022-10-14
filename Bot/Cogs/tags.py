import os
import urllib.parse

import discord
from akari_tags_utils import AkariTags, AkariTagsUtils
from akari_ui_components import PurgeAllTagsView, RemoveTagModal
from discord.commands import Option, SlashCommandGroup
from discord.ext import commands
from dotenv import load_dotenv
from rin_exceptions import ItemNotFound
from tortoise import Tortoise
from tortoise.transactions import in_transaction

load_dotenv()

POSTGRES_USER = os.getenv("Postgres_User")
POSTGRES_PASSWORD = urllib.parse.quote_plus(os.getenv("Postgres_Password"))
POSTGRES_HOST = os.getenv("Postgres_Host")
POSTGRES_PORT = os.getenv("Postgres_Port")
POSTGRES_DB = os.getenv("Postgres_Akari_DB")
CONNECTION_URI = f"asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

tagsUtils = AkariTagsUtils(uri=CONNECTION_URI, models=["akari_tags_utils.models"])


class Tags(commands.Cog):
    """Commands for managing tags, and for displaying tags."""

    def __init__(self, bot):
        self.bot = bot
        self.uri = CONNECTION_URI

    tags = SlashCommandGroup(
        "tags", "Commands for managing tags", guild_ids=[970159505390325842]
    )
    tagsView = tags.create_subgroup(
        "view", "Commands for viewing tags", guild_ids=[970159505390325842]
    )
    tagsDelete = tags.create_subgroup(
        "delete", "Commands for deleting tags", guild_ids=[970159505390325842]
    )

    @tagsView.command(name="one")
    async def viewTagsOne(self, ctx, *, name: Option(str, "The tag name to view")):
        """View one tag within a server"""
        await Tortoise.init(
            db_url=self.uri, modules={"models": ["akari_tags_utils.models"]}
        )
        async with in_transaction() as connection:
            data = (
                await AkariTags.filter(tag_name=name)
                .using_db(connection)
                .first()
                .values()
            )
            try:
                if data is None:
                    raise ItemNotFound
                else:
                    embed = discord.Embed()
                    embed.title = data["tag_name"]
                    embed.description = data["tag_content"]
                    embed.add_field(
                        name="Created At (UTC)",
                        value=data["created_at"].strftime("%Y-%m-%d %H:%M:%S"),
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

    @tagsView.command(name="all")
    async def viewTagsOne(self, ctx):
        """Views all tag within a server"""
        await Tortoise.init(
            db_url=self.uri, modules={"models": ["akari_tags_utils.models"]}
        )
        async with in_transaction() as connection:
            data = (
                await AkariTags.filter(guild_id=ctx.guild.id)
                .using_db(connection)
                .all()
                .values()
            )
            await ctx.respond(data)

    @tagsDelete.command(name="one")
    async def deleteOneTag(self, ctx):
        """Deletes one tag within a server"""
        mainModal = RemoveTagModal(
            uri=self.uri, models=["akari_tags_utils.models"], title="Tag Removal"
        )
        await ctx.send_modal(mainModal)

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
        )


def setup(bot):
    bot.add_cog(Tags(bot))
