import discord
from discord import app_commands
from discord.ext import commands


# This whole idea was taken from Pycord's Toolkit bot, but modified to work with discord.py
# This system is also used on Kumiko as well
class HelpSelect(discord.ui.Select):
    def __init__(self, bot) -> None:
        self.bot = bot
        options = [
            discord.SelectOption(label=cog_name, description=cog.__doc__)
            for cog_name, cog in sorted(bot.cogs.items())
            if cog_name not in ["PingRedis"]
        ]
        super().__init__(
            placeholder="Select a category",
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        cog = self.bot.get_cog(self.values[0])
        embed = discord.Embed(
            title=f"{cog.__cog_name__} Commands",
            description="\n".join(
                f"`/{command.qualified_name}`: {command.description}"
                for command in cog.walk_app_commands()
            ),
            color=discord.Color.from_rgb(255, 145, 244),
            timestamp=discord.utils.utcnow(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


class Help(commands.Cog):
    """Commands for getting commands for Akari"""

    def __init__(self, bot):
        self.bot = bot

    # Precondition: There must be at the very least one cog loaded
    @app_commands.command(name="help")
    async def akariHelp(self, interaction: discord.Interaction):
        """Shows all commands available"""
        embed = discord.Embed()
        embed.title = "Help"
        view = discord.ui.View().add_item(HelpSelect(self.bot))
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Help(bot))
