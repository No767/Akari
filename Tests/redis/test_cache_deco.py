import sys
from pathlib import Path

import pytest

path = Path(__file__).parents[2].joinpath("Bot")
sys.path.append(str(path))

from Libs.cache import cache, cacheJson
from redis.asyncio.connection import ConnectionPool


@pytest.mark.asyncio
async def test_cache_deco():
    connPool = ConnectionPool(max_connections=25)

    @cache(connection_pool=connPool)
    async def testFunc(id):
        return "Hello World"

    res = await testFunc(5265)
    assert (res == "Hello World") and isinstance(res, str)  # nosec


@pytest.mark.asyncio
async def test_cache_deco_json():
    connPool = ConnectionPool(max_connections=25)

    @cacheJson(connection_pool=connPool)
    async def testFuncJSON(id=234):
        return {"message": "Hello World"}

    res = await testFuncJSON(23423)
    assert (res == {"message": "Hello World"}) and isinstance(res, dict)  # nosec
