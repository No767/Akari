import discord
from discord.commands import Option, SlashCommandGroup
from discord.ext import commands
import platform


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    info = SlashCommandGroup(
        "info", "Gets the information needed of the user", guild_ids=[970159505390325842]
    )

    @info.command(name="user")
    async def getUserInfo(
        self, ctx, *, user: Option(discord.Member, "The user to get the info of")
    ):
        """Gets info about the requested user"""
        embed = discord.Embed()
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.title = user.display_name
        embed.add_field(
            name="On Nitro Since (UTC)",
            value=user.premium_since.strftime("%Y-%m-%d %H:%M:%S")
            if user.premium_since is not None
            else None,
            inline=True,
        )
        embed.add_field(
            name="Account Creation Date (UTC)",
            value=user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            inline=True,
        )
        embed.add_field(
            name="Server Join Date (UTC)",
            value=user.joined_at.strftime("%Y-%m-%d %H:%M:%S")
            if user.joined_at is not None
            else None,
            inline=True,
        )
        embed.add_field(
            name="Timeout Since",
            value=user.communication_disabled_until.strftime("%Y-%m-%d %H:%M:%S")
            if user.communication_disabled_until is not None
            else None,
            inline=True,
        )
        embed.add_field(
            name="Roles",
            value=str([roleName.name for roleName in user.roles][1:]).replace(
                "'", ""
            ),
            inline=True,
        )
        embed.add_field(
            name="Desktop Status", value=user.desktop_status, inline=True
        )
        embed.add_field(name="Web Status", value=user.web_status, inline=True)
        embed.add_field(name="On Mobile?", value=user.is_on_mobile(), inline=True)
        embed.add_field(name="Bot?", value=user.bot, inline=True)
        embed.add_field(name="Top Role", value=user.top_role.name, inline=True)
        embed.add_field(
            name="Mutual Guilds",
            value=str([guilds.name for guilds in user.mutual_guilds]).replace(
                "'", ""
            ),
            inline=True,
        )
        embed.add_field(name="Guild Nickname", value=user.nick, inline=True)
        embed.add_field(name="On Timeout?", value=user.timed_out, inline=True)
        await ctx.respond(embed=embed)
        
    @info.command(name="bot")
    async def botInfo(self, ctx):
        """Gets any info about the bot"""
        embed = discord.Embed()
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.title = self.bot.user.name
        embed.add_field(name="Server Count", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Users Count", value=len(self.bot.users), inline=True)
        embed.add_field(name="System", value=platform.system(), inline=True)
        embed.add_field(name="Python Compiler", value=platform.python_compiler(), inline=True)
        embed.add_field(name="Python Version", value=platform.python_version(), inline=True)
        embed.add_field(name="Pycord Version", value=discord.__version__, inline=True)
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Info(bot))