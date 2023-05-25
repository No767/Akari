from typing import Union

import asyncpg

from ..cache import akariCPM, cache, cacheJson

# from prisma import types  # type: ignore
# from prisma.models import Guild, Tag  # type: ignore


@cacheJson(
    connection_pool=akariCPM.getConnPool(),
)
async def getGuildTag(id: int, tag_name: str, pool: asyncpg.Pool) -> Union[dict, None]:
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
    WHERE g.id=$1 AND t.name=$2;
    """
    async with pool.acquire() as conn:
        res = await conn.fetchrow(sqlQuery, id, tag_name)
        if res is None:
            return None
        return dict(res)


@cache(
    connection_pool=akariCPM.getConnPool(),
)
async def getGuildTagText(
    id: int, tag_name: str, pool: asyncpg.Pool
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
    WHERE g.id=$1 AND t.name=$2;
    """
    async with pool.acquire() as conn:
        res = await conn.fetchval(sqlQuery, id, tag_name)
        if res is None:
            return None
        return res


@cacheJson(
    connection_pool=akariCPM.getConnPool(),
)
async def listGuildTags(id: Union[int, None]):
    # trueID = id if id is not None else 0
    # res = await Guild.prisma().find_unique(where={"id": trueID}, include={"tags": True})
    # if res is None:
    #     return None
    # return res.dict()
    return None
