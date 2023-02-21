import discord
from prisma.models import Guild  # type: ignore


class CreateTag(discord.ui.Modal, title="Create a tag"):
    name = discord.ui.TextInput(
        label="Name", placeholder="Name of the tag", min_length=1, max_length=25, row=0
    )
    content = discord.ui.TextInput(
        label="Content",
        style=discord.TextStyle.long,
        placeholder="Content of the tag",
        min_length=1,
        max_length=300,
        row=1,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await Guild.prisma().update(
            data={
                "tags": {
                    "create": [{"name": self.name.value, "content": self.content.value}]
                }
            },
            where={"id": interaction.guild.id},  # type: ignore
        )

        await interaction.response.send_message("Tag created", ephemeral=True)

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        await interaction.response.send_message(
            f"An error occurred ({error.__class__.__name__})", ephemeral=True
        )
