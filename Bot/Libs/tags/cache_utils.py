from typing import Any, Dict, List, Union

import asyncpg
from redis.asyncio.connection import ConnectionPool

from ..cache import cache, cacheJson
from ..utils import encodeDatetime


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
    async with db_pool.acquire() as conn:
        res = await conn.fetchrow(sqlQuery, id, tag_name, [tag_name])
        if res is None:
            return None
        return encodeDatetime(dict(res))


@cache()
async def getGuildTagText(
    id: int, redis_pool: ConnectionPool, tag_name: str, db_pool: asyncpg.Pool
) -> Union[str, None]:
    """Gets a tag from the database. This is the raw text that will be cached

    Args:
        id (int): Guild ID
        tag_name (str): Tag name

    Returns:
        Union[str, None]: The tag content or None if it doesn't exist
    """
    sqlQuery = """
    SELECT DISTINCT ON (g.id)
        t.content
    FROM guild g
    INNER JOIN tag t ON g.id = t.guild_id
    WHERE g.id=$1 AND t.name=$2 OR aliases @> $3;
    """
    async with db_pool.acquire() as conn:
        res = await conn.fetchval(sqlQuery, id, tag_name, [tag_name])
        if res is None:
            return None
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
