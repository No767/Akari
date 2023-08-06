from typing import Dict, List, Union

import asyncpg


async def edit_tag(
    guild_id: int, author_id: int, name: str, content: str, pool: asyncpg.Pool
) -> str:
    query = """
    UPDATE tag
    SET content = $1
    WHERE guild_id = $3 AND LOWER(tag.name) = $2 AND author_id = $4;
    """
    status = await pool.execute(query, content, name, guild_id, author_id)
    return status


async def get_tag_content(id: int, name: str, pool: asyncpg.Pool):
    init_query = """
    SELECT tag.content
    FROM tag_lookup
    INNER JOIN tag ON tag.id = tag_lookup.tag_id
    WHERE tag_lookup.guild_id=$1 AND LOWER(tag_lookup.name)=$2 OR LOWER($2) = ANY(aliases); 
    """
    async with pool.acquire() as conn:
        res = await conn.fetchval(init_query, id, name)
        if res is None:
            query = """
            SELECT     tag_lookup.name
            FROM       tag_lookup
            WHERE      tag_lookup.guild_id=$1 AND tag_lookup.name % $2 OR $2 = ANY(aliases)
            ORDER BY   similarity(tag_lookup.name, $2) DESC
            LIMIT 5;
            """
            new_res = await conn.fetch(query, id, name)
            if new_res is None or len(new_res) == 0:
                return None

            return [dict(row) for row in new_res]
        return res


async def get_tag_info(id: int, name: str, pool: asyncpg.Pool):
    query = """
    SELECT tag.name, tag.content, tag.created_at, tag.author_id, tag_lookup.aliases
    FROM tag_lookup
    INNER JOIN tag ON tag.id = tag_lookup.tag_id
    WHERE tag_lookup.guild_id=$1 AND LOWER(tag_lookup.name)=$2 OR LOWER(tag_lookup.name) = ANY(aliases);
    """
    res = await pool.fetchrow(query, id, name)
    if res is None:
        return None
    return dict(res)


async def create_tag(
    author_id: int, guild_id: int, pool: asyncpg.Pool, name: str, content: str
) -> str:
    """Creates a tag from the given info

    Args:
        author_id (int): The user's ID
        guild_id (int): The guild's ID
        pool (asyncpg.Pool): Asyncpg connection pool
        name (str): The name of the tag
        content (str): The contents of the tag

    Returns:
        str: The status of whether it was successful or not
    """

    query = """WITH tag_insert AS (
            INSERT INTO tag (author_id, guild_id, name, content) 
            VALUES ($1, $2, $3, $4)
            RETURNING id
        )
        INSERT INTO tag_lookup (name, owner_id, guild_id, tag_id)
        VALUES ($3, $1, $2, (SELECT id FROM tag_insert));
    """
    async with pool.acquire() as conn:
        tr = conn.transaction()
        await tr.start()
        try:
            await conn.execute(
                query,
                author_id,
                guild_id,
                name,
                content,
            )
        except asyncpg.UniqueViolationError:
            await tr.rollback()
            return f"The tag (`{name}`) already exists."
        except Exception:
            await tr.rollback()
            return "Could not create tag"
        else:
            await tr.commit()
            return f"Tag `{name}` successfully created"


async def get_all_tags(guild_id: int, pool: asyncpg.Pool):
    query = """
    SELECT tag.id, tag.name, tag_lookup.aliases, tag.content, tag.created_at, tag.author_id
    FROM tag_lookup
    INNER JOIN tag ON tag.id = tag_lookup tag_id
    WHERE tag_lookup.guild_id=$1;
    """
    rows = await pool.fetch(query, guild_id)
    if rows is None:
        return []
    return rows


async def get_owned_tags(
    author_id: int, guild_id: int, pool: asyncpg.Pool
) -> Union[List[asyncpg.Record], List]:
    query = """
    SELECT tag.name, tag.id
    FROM tag_lookup
    INNER JOIN tag ON tag.id = tag_lookup.tag_id
    WHERE tag_lookup.guild_id=$1 AND tag_lookup.owner_id=$2;
    """
    rows = await pool.fetch(query, guild_id, author_id)
    if rows is None:
        return []
    return rows


def format_options(rows: Union[List[Dict[str, str]], None]) -> str:
    """Format the rows to be sent to the user

    Args:
        rows (Union[List[Dict[str, str]], None]): Rows to format

    Returns:
        str: Formatted string
    """
    if rows is None or len(rows) == 0:
        return "Tag not found"

    names = "\n".join([row["name"] for row in rows])
    return f"Tag not found. Did you mean:\n{names}"
