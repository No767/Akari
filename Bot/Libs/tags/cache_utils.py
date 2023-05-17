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
    res = await Guild.prisma().find_first(
        where={
            "AND": [{"id": id}, {"tags": {"every": {"name": {"contains": tag_name}}}}]
        },
        include={"tags": True},
    )
    if res is None:
        return None
    return res.dict()


@cache(
    connection_pool=akariCPM.getConnPool(),
)
async def getGuildTagText(id: Union[int, None], tag_name: str) -> Union[str, None]:
    """Gets a tag from the database. This is the raw text that will be cached

    Args:
        id (int): Guild ID
        tag_name (str): Tag name

    Returns:
        Union[str, None]: The tag content or None if it doesn't exist
    """
    trueID = id if id is not None else 0
    res = await Guild.prisma().find_first(
        where={
            "AND": [
                {"id": trueID},
                {"tags": {"every": {"name": {"contains": tag_name}}}},
            ]
        },
        include={"tags": True},
    )
    if res is None:
        return None
    return res.tags[0].content if res.tags is not None else "None"


@cacheJson(
    connection_pool=akariCPM.getConnPool(),
)
async def listGuildTags(id: Union[int, None]):
    trueID = id if id is not None else 0
    res = await Guild.prisma().find_unique(where={"id": trueID}, include={"tags": True})
    if res is None:
        return None
    return res.dict()
