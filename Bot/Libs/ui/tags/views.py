import asyncpg
import discord
from Libs.utils import CancelledEmbed, ConfirmEmbed


class DeleteTag(discord.ui.View):
    def __init__(self, pool: asyncpg.Pool, tag_name: str) -> None:
        super().__init__()
        self.pool: asyncpg.Pool = pool
        self.tag_name = tag_name

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        deleteQuery = """
        DELETE FROM tag WHERE guild_id=$1 AND author_id=$2 AND name=$3;
        """
        async with self.pool.acquire() as conn:
            await conn.execute(deleteQuery, interaction.guild.id, interaction.user.id, self.tag_name)  # type: ignore
            for item in self.children:
                item.disabled = True  # type: ignore

            await interaction.response.edit_message(
                embed=ConfirmEmbed(description="Tag deleted"), view=self
            )
            self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        for item in self.children:
            item.disabled = True  # type: ignore
        await interaction.response.edit_message(
            embed=CancelledEmbed(description="The action was cancelled"), view=self
        )
        self.stop()
