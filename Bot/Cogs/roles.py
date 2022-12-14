import os
import urllib.parse

import discord
from akari_ui_components import InitConfirmRolesSetupView
from discord.commands import Option, SlashCommandGroup
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("Redis_Host")
REDIS_PORT = os.getenv("Redis_Port")
POSTGRES_USER = os.getenv("Postgres_User")
POSTGRES_PASSWORD = urllib.parse.quote_plus(os.getenv("Postgres_Password"))
POSTGRES_HOST = os.getenv("Postgres_Host")
POSTGRES_PORT = os.getenv("Postgres_Port")
POSTGRES_DB = os.getenv("Postgres_Akari_DB")
CONNECTION_URI = f"asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
MODELS = ["akari_modmail.models", "akari_servers.models"]

DEFAULT_PERMS = discord.Permissions(
    view_channel=True,
    add_reactions=True,
    change_nickname=True,
    embed_links=True,
    external_emojis=True,
    external_stickers=True,
    read_message_history=True,
    send_messages=True,
    speak=True,
    use_application_commands=True,
    use_voice_activation=True,
)


class Roles(commands.Cog):
    """Commands for managing and viewing roles"""

    def __init__(self, bot):
        self.bot = bot

    roles = SlashCommandGroup(
        "roles",
        "Commands for managing and viewing roles",
        guild_ids=[970159505390325842],
    )

    @roles.command(name="setup")
    async def setupRoles(self, ctx: discord.ApplicationContext):
        """Set up the dropdown roles"""
        view = InitConfirmRolesSetupView(
            uri=CONNECTION_URI,
            models=MODELS,
            redis_host=REDIS_HOST,
            redis_port=REDIS_PORT,
            command_name=ctx.command.qualified_name,
        )
        await ctx.respond("test", view=view)

    @roles.command(name="list")
    async def getRolesList(self, ctx):
        """List all roles in the server"""
        guildRoles = ctx.guild.roles
        embed = discord.Embed()
        embed.title = f"{ctx.guild.name} Roles"
        embed.description = "\n".join(
            f"{role.icon.url if role.icon is not None else ''} {role.name}"
            for role in guildRoles
            if role.name not in ["@everyone", "Akari-Dev"]
        )
        await ctx.respond(embed=embed)

    @roles.command(name="add")
    async def addRole(
        self,
        ctx,
        *,
        name: Option(str, "The role's name"),
        mentionable: Option(bool, "Whether the role is mentionable", default=False),
        hoist: Option(bool, "Whether the role is hoisted", default=True),
    ):
        """Adds a new role to the current server"""
        await ctx.guild.create_role(
            name=name, permissions=DEFAULT_PERMS, mentionable=mentionable, hoist=hoist
        )
        await ctx.respond(f"Successfully created role {name}")

    @roles.command(name="edit")
    async def editRole(
        self,
        ctx,
        *,
        role: Option(discord.Role, "The role to edit"),
        name: Option(str, "The role's new name"),
        mentionable: Option(bool, "Whether the role is mentionable", default=False),
        hoist: Option(bool, "Whether the role is hoisted", default=True),
    ):
        """Edits a role"""
        topRole = await ctx.guild.roles[-1]
        if role < topRole:
            await role.edit(
                name=name,
                permissions=DEFAULT_PERMS,
                color=discord.Color.default(),
                mentionable=mentionable,
                hoist=hoist,
            )
            await ctx.respond(f"Successfully edited role {name}")
        else:
            await ctx.respond("You cannot edit a role higher than your highest role")

    @roles.command(name="delete")
    async def deleteRole(
        self, ctx, *, role: Option(discord.Role, "The role to delete")
    ):
        """Deletes a role"""
        await role.delete()
        await ctx.respond(f"Successfully deleted role {role.name}")

    @roles.command(name="view")
    async def viewRole(self, ctx, *, role: Option(discord.Role, "The role to select")):
        """Views a role"""
        embed = discord.Embed()
        embed.color = role.color.to_rgb()
        embed.title = role.name
        embed.add_field(
            name="Created At", value=discord.utils.format_dt(role.created_at)
        )
        embed.add_field(name="Hoist?", value=role.hoist)
        embed.add_field(name="Mentionable?", value=role.mentionable)
        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Roles(bot))
