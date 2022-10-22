import asyncio
import os
import sys
import urllib.parse
import uuid
from datetime import timedelta
from pathlib import Path

import discord
import uvloop
from discord.commands import Option, SlashCommandGroup
from discord.ext import commands, pages
from dotenv import load_dotenv
from pytimeparse.timeparse import timeparse
from rin_exceptions import NoItemsError

path = Path(__file__).parents[1].absolute()
packagePath = os.path.join(str(path), "Libs")
envPath = os.path.join(str(path), ".env")
sys.path.append(packagePath)

load_dotenv(dotenv_path=envPath)

from akari_admin_logs import AkariAdminLogsUtils
from akari_ui_components import PurgeALDataView

POSTGRES_USER = os.getenv("Postgres_User")
POSTGRES_PASSWORD = urllib.parse.quote_plus(os.getenv("Postgres_Password"))
POSTGRES_HOST = os.getenv("Postgres_Host")
POSTGRES_PORT = os.getenv("Postgres_Port")
POSTGRES_DB = os.getenv("Postgres_Akari_DB")
CONNECTION_URI = f"asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

alUtils = AkariAdminLogsUtils(uri=CONNECTION_URI, models=["akari_admin_logs.models"])


class Admin(commands.Cog):
    """A set of administrative commands"""

    def __init__(self, bot):
        self.bot = bot

    admin = SlashCommandGroup("admin", "Admin commands")
    adminTimeout = admin.create_subgroup("timeout", "Timeouts commands")
    adminLogs = admin.create_subgroup("logs", "Admin logs")

    @admin.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def banMembers(
        self,
        ctx,
        *,
        user: Option(discord.Member, "The user to ban"),
        reason: Option(str, "The reason for the ban"),
    ):
        """Bans the requested user"""
        await alUtils.addALRow(
            uuid=uuid.uuid4(),
            guild_id=ctx.guild.id,
            action_username=ctx.user.name,
            affected_username=user.name,
            type_of_action="ban",
            reason=reason,
            date_issued=discord.utils.utcnow(),
            duration=999,
        )
        await user.ban(delete_message_days=7, reason=reason)
        embed = discord.Embed(
            title=f"Banned {user.name}", color=discord.Color.from_rgb(255, 51, 51)
        )
        embed.description = (
            f"**Successfully banned {user.name}**\n\n**Reason:** {reason}"
        )
        await ctx.respond(embed=embed)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    @admin.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unbanMembers(
        self,
        ctx,
        *,
        user: Option(discord.Member, "The user to unban"),
        reason: Option(str, "The reason for the unban"),
    ):
        """Un-bans the requested user"""
        await alUtils.addALRow(
            uuid=uuid.uuid4(),
            guild_id=ctx.guild.id,
            action_username=ctx.user.name,
            affected_username=user.name,
            type_of_action="unban",
            reason=reason,
            date_issued=discord.utils.utcnow(),
            duration=999,
        )
        await ctx.guild.unban(user=user, reason=reason)
        embed = discord.Embed(
            title=f"Unbanned {user.name}", color=discord.Color.from_rgb(178, 171, 255)
        )
        embed.description = (
            f"**Successfully unbanned {user.name}**\n\n**Reason:** {reason}"
        )
        await ctx.respond(embed=embed, ephemeral=True)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    @admin.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kickUser(
        self,
        ctx,
        *,
        user: Option(discord.Member, "The user to kick out of the server"),
        reason: Option(str, "The reason for why"),
    ):
        """Kicks the requested user"""
        await alUtils.addALRow(
            uuid=uuid.uuid4(),
            guild_id=ctx.guild.id,
            action_username=ctx.user.name,
            affected_username=user.name,
            type_of_action="kick",
            reason=reason,
            date_issued=discord.utils.utcnow(),
            duration=0,
        )
        await user.kick(reason=reason)
        embed = discord.Embed(
            title=f"Kicked {user.name}", color=discord.Color.from_rgb(206, 255, 186)
        )
        embed.description = (
            f"**Successfully kicked {user.name}**\n\n**Reason:** {reason}"
        )
        await ctx.respond(embed=embed, ephemeral=True)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    @adminTimeout.command(name="duration")
    @commands.has_permissions(moderate_members=True)
    async def timeoutDuration(
        self,
        ctx,
        *,
        user: Option(discord.Member, "The user to timeout"),
        duration: Option(str, "The duration of the timeout"),
        reason: Option(str, "The reason for the timeout", default=None),
    ):
        """Applies a timeout to the user for a specified amount of time"""
        try:
            parsedTime = timeparse(duration)
            timeoutDuration = timedelta(seconds=parsedTime)
            await alUtils.addALRow(
                uuid=uuid.uuid4(),
                guild_id=ctx.guild.id,
                action_username=ctx.user.name,
                affected_username=user.name,
                type_of_action="timeout",
                reason=reason,
                date_issued=discord.utils.utcnow(),
                duration=timeoutDuration,
            )
            await user.timeout_for(duration=timeoutDuration, reason=reason)
            embed = discord.Embed(
                title=f"Timeout applied for {user.name}",
                color=discord.Color.from_rgb(255, 255, 102),
            )
            embed.description = f"{user.name }has been successfully timed out for {timeoutDuration}\n\n**Reason:** {reason}"
            await ctx.respond(embed=embed, ephemeral=True)
        except TypeError:
            await ctx.respond(
                embed=discord.Embed(
                    description="It seems like you may have mistyped the amount of time for the timeout. Some examples that you can use are the following: `1h`, `1d`, `2 hours`, `5d`"
                )
            )

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    @adminTimeout.command(name="remove")
    @commands.has_permissions(moderate_members=True)
    async def removeTimeout(
        self,
        ctx,
        *,
        user: Option(discord.Member, "The user to remove the timeout from"),
        reason: Option(str, "The reason why the timeout should be removed"),
    ):
        """Removes the timeout from the user"""
        await alUtils.addALRow(
            uuid=uuid.uuid4(),
            guild_id=ctx.guild.id,
            action_username=ctx.user.name,
            affected_username=user.name,
            type_of_action="timeout-remove",
            reason=reason,
            date_issued=discord.utils.utcnow(),
            duration=0,
        )
        await user.remove_timeout(reason=reason)
        embed = discord.Embed(
            title=f"Timeout removed for {user.name}",
            color=discord.Color.from_rgb(255, 251, 194),
        )
        embed.description = f"Timeout for {user.name} has been successfully removed\n\n**Reason:** {reason}"
        await ctx.respond(embed=embed, ephemeral=True)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    @adminLogs.command(name="view")
    @commands.has_permissions(moderate_members=True)
    async def viewAL(
        self,
        ctx,
        *,
        filter: Option(
            str,
            "The filters to apply",
            choices=["All", "Ban", "Unban", "Kick", "Timeout", "Timeout-Remove"],
        ),
    ):
        """Views the Admin Logs"""
        logsData = await alUtils.getAllALData(guild_id=ctx.guild.id)
        if filter not in ["All"]:
            logsData = await alUtils.getLogsFiltered(
                guild_id=ctx.guild.id, type_of_action=str(filter).lower()
            )
        try:
            if len(logsData) == 0:
                raise NoItemsError
            else:
                mainPages = pages.Paginator(
                    pages=[
                        discord.Embed(
                            title=f"{dict(item)['type_of_action'].title()} - {dict(item)['affected_username']}",
                            description=dict(item)["reason"],
                        )
                        .add_field(name="Issuer", value=dict(item)["action_username"])
                        .add_field(
                            name="Date Issued",
                            value=dict(item)["date_issued"].strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                        )
                        .add_field(name="Duration", value=dict(item)["duration"])
                        for item in logsData
                    ],
                    loop_pages=True,
                )
                await mainPages.respond(ctx.interaction, ephemeral=True)
        except NoItemsError:
            await ctx.respond(
                embed=discord.Embed(
                    description="There are no logs to display so far. Please try again"
                ),
                ephemeral=True,
            )

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    @adminLogs.command(name="purge")
    @commands.has_permissions(moderate_members=True)
    async def purgeALData(self, ctx):
        """Purges all Admin Logs for that guild"""
        embed = discord.Embed()
        embed.description = (
            "Are you sure you want to purge all Admin Logs for this guild?"
        )
        await ctx.respond(
            embed=embed,
            view=PurgeALDataView(
                uri=CONNECTION_URI, models=["akari_admin_logs.models"]
            ),
            ephemeral=True,
        )

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def setup(bot):
    bot.add_cog(Admin(bot))
