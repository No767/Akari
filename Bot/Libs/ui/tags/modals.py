import asyncpg
import discord


class CreateTag(discord.ui.Modal, title="Create a tag"):
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


class EditTag(discord.ui.Modal, title="Edit a tag"):
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
        sqlQuery = """
        UPDATE tag 
        SET content = $2
        WHERE name=$1;
        """
        async with self.pool.acquire() as conn:
            await conn.execute(sqlQuery, self.name.value, self.content.value)
            await interaction.response.send_message("Tag edited", ephemeral=True)
