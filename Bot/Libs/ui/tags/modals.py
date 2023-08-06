import asyncpg
import discord


class CreateTagModal(discord.ui.Modal, title="Create a tag"):
    def __init__(self, pool: asyncpg.pool.Pool) -> None:
        super().__init__()
        self.pool: asyncpg.Pool = pool
        self.name = discord.ui.TextInput(
            label="Name",
            placeholder="Name of the tag",
            min_length=1,
            max_length=25,
            row=0,
        )
        self.content = discord.ui.TextInput(
            label="Content",
            style=discord.TextStyle.long,
            placeholder="Content of the tag",
            min_length=1,
            max_length=300,
            row=1,
        )
        self.add_item(self.name)
        self.add_item(self.content)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        # Ripped the whole thing from RDanny again...
        insertQuery = """WITH tag_insert AS (
            INSERT INTO tag (author_id, guild_id, name, content) 
            VALUES ($1, $2, $3, $4)
            RETURNING id
        )
        INSERT INTO tag_lookup (name, owner_id, guild_id, tag_id)
        VALUES ($3, $1, $2, (SELECT id FROM tag_insert));
        """
        async with self.pool.acquire() as conn:
            tr = conn.transaction()
            await tr.start()

            try:
                await conn.execute(
                    insertQuery,
                    interaction.user.id,
                    interaction.guild.id,  # type: ignore
                    self.name.value,
                    self.content.value,
                )
            except asyncpg.UniqueViolationError:
                await tr.rollback()
                await interaction.response.send_message("This tag already exists.")
            except:
                await tr.rollback()
                await interaction.response.send_message("Could not create tag.")
            else:
                await tr.commit()
                await interaction.response.send_message(
                    f"Tag {self.name} successfully created."
                )

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        await interaction.response.send_message(
            f"An error occurred ({error.__class__.__name__})", ephemeral=True
        )


class EditTagModal(discord.ui.Modal, title="Edit a tag"):
    def __init__(self, pool: asyncpg.pool.Pool) -> None:
        super().__init__()
        self.pool: asyncpg.Pool = pool
        self.name = discord.ui.TextInput(
            label="Name",
            placeholder="Name of the tag",
            min_length=1,
            max_length=25,
            row=0,
        )
        self.content = discord.ui.TextInput(
            label="Content",
            style=discord.TextStyle.long,
            placeholder="Content of the tag",
            min_length=1,
            max_length=300,
            row=1,
        )
        self.add_item(self.name)
        self.add_item(self.content)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        # OR aliases @> $ - To check for aliases
        query = """
        UPDATE tag
        SET content = $1
        WHERE guild_id = $3 AND LOWER(tag.name) = $2 AND author_id = $4;
        """
        if interaction.guild is None:
            await interaction.response.send_message(
                "You can't do this in a DM", ephemeral=True
            )
            return
        await self.pool.execute(
            query,
            self.content.value,
            self.name.value,
            interaction.guild.id,
            interaction.user.id,
        )
        await interaction.response.send_message(
            f"Tag `{self.name.value}` edited", ephemeral=True
        )
        return
