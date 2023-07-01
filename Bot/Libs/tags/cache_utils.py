from typing import Any, Dict, List, TypedDict, Union

import asyncpg
from redis.asyncio.connection import ConnectionPool

from ..cache import cache, cacheJson
from ..utils import encodeDatetime


class TagEntry(TypedDict):
    id: int
    name: str
    content: str


@cacheJson()
async def getGuildTag(
    id: int, redis_pool: ConnectionPool, tag_name: str, db_pool: asyncpg.Pool
) -> Union[dict, None]:
    """Gets a tag from the database. This is the JSON model that will be cached

    Args:
        id (int): Guild ID
        tag_name (str): Tag name
        pool (asyncpg.Pool): Asyncpg Connection Pool to pull conns from

    Returns:
        Union[Dict, None]: The tag content or None if it doesn't exist
    """
    sqlQuery = """
    SELECT DISTINCT ON (g.id)
        t.id, t.author_id, t.name, t.aliases, t.created_at
    FROM guild g
    INNER JOIN tag t ON g.id = t.guild_id
    WHERE g.id=$1 AND t.name=$2 OR aliases @> $3;
    """
    sqlQuery = """
    SELECT tag.name, tag.content
    FROM tag_lookup
    INNER JOIN tag ON tag.id = tag_lookup.tag_id
    WHERE tag_lookup.guild_id=970159505390325842 AND LOWER(tag_lookup.name)='uwu';
    """
    async with db_pool.acquire() as conn:
        res = await conn.fetchrow(sqlQuery, id, tag_name, [tag_name])
        if res is None:
            return None
        return encodeDatetime(dict(res))


@cache()
async def getGuildTagText(
    id: int, redis_pool: ConnectionPool, tag_name: str, db_pool: asyncpg.Pool
) -> Union[str, dict, None]:
    """Gets a tag from the database. This is the raw text that will be cached

    Args:
        id (int): Guild ID
        tag_name (str): Tag name

    Returns:
        Union[str, None]: The tag content or None if it doesn't exist
    """
    sqlQuery = """
    SELECT tag.content
    FROM tag_lookup
    INNER JOIN tag ON tag.id = tag_lookup.tag_id
    WHERE tag_lookup.guild_id=$1 AND LOWER(tag_lookup.name)=$2;
    """
    # That's the old one below
    # """    SELECT DISTINCT ON (g.id)
    #     t.content
    # FROM guild g
    # INNER JOIN tag t ON g.id = t.guild_id
    # WHERE g.id=$1 AND t.name=$2 OR aliases @> $3;
    # """
    async with db_pool.acquire() as conn:
        # [tag_name]
        res = await conn.fetchval(sqlQuery, id, tag_name)
        if res is None:
            query = """
            SELECT     tag_lookup.name
            FROM       tag_lookup
            WHERE      tag_lookup.guild_id=$1 AND tag_lookup.name % $2
            ORDER BY   similarity(tag_lookup.name, $2) DESC
            LIMIT 5;
            """
            newRes = await conn.fetch(query, id, tag_name)

            if newRes is None or len(newRes) == 0:
                return None

            return dict(newRes)
        return res


@cacheJson(ttl=120)
async def listGuildTags(
    id: int, redis_pool: ConnectionPool, db_pool: asyncpg.Pool
) -> List[Dict[str, Any]]:
    """Returns a list of all of the tags that the guild owns

    Args:
        id (int): Guild ID
        pool (asyncpg.Pool): Asyncpg connection pool

    Returns:
        List[Dict[str, Any]]: A list of all of the tags that the guild owns
    """
    query = """
    SELECT t.id, t.author_id, t.name, t.aliases, t.content, t.created_at
    FROM guild g
    INNER JOIN tag t ON g.id = t.guild_id
    WHERE g.id=$1;
    """
    async with db_pool.acquire() as conn:
        res = await conn.fetch(query, id)
        return [encodeDatetime(dict(row)) for row in res]
