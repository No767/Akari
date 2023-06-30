import sys
from pathlib import Path

import pytest
from redis.asyncio.connection import ConnectionPool

path = Path(__file__).parents[2].joinpath("Bot")
sys.path.append(str(path))

from Libs.cache import AkariCPM
from Libs.utils.redis import openConnCheck, pingRedisServer


@pytest.mark.asyncio
async def test_ping_redis():
    cpm = AkariCPM(uri="redis://localhost:6379")
    connPool = cpm.getConnPool()
    res = await pingRedisServer(connection_pool=connPool)

    assert res is True


@pytest.mark.asyncio
async def test_open_conn_check():
    connPool = ConnectionPool().from_url("redis://localhost:6379")
    result = await openConnCheck(connection_pool=connPool)
    assert result is True
