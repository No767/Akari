from typing import Dict, Union

from prisma import types  # type: ignore
from prisma.models import Guild, Tag  # type: ignore

from ..cache import akariCPM, cache, cacheJson


@cacheJson(
    connection_pool=akariCPM.getConnPool(),
)
async def getGuildTag(id: int, tag_name: str) -> Union[Dict, None]:
    """Gets a tag from the database. This is the JSON model that will be cached

    Args:
        id (int): Guild ID
        tag_name (str): Tag name

    Returns:
        Union[Dict, None]: The tag content or None if it doesn't exist
    """
    res = await Tag.prisma().find_first(
        where={
            "AND": [
                {"guild_id": {"equals": id}},
                {"name": {"contains": tag_name}},
            ]
        }
    )
    if res is None:
        return None
    return res.to_dict()


@cache(
    connection_pool=akariCPM.getConnPool(),
)
async def getGuildTagText(id: int, tag_name: str) -> Union[str, None]:
    """Gets a tag from the database. This is the raw text that will be cached

    Args:
        id (int): Guild ID
        tag_name (str): Tag name

    Returns:
        Union[str, None]: The tag content or None if it doesn't exist
    """
    res = await Tag.prisma().find_first(
        where={
            "AND": [
                {"guild_id": {"equals": id}},
                {"name": {"contains": tag_name}},
            ]
        }
    )
    if res is None:
        return None
    return res.content
