import sys
from pathlib import Path

import pytest
from redis.asyncio.connection import ConnectionPool

path = Path(__file__).parents[2].joinpath("Bot")
sys.path.append(str(path))

from Libs.utils.redis import openConnCheck


@pytest.mark.asyncio
async def test_open_conn_check():
    connPool = ConnectionPool().from_url("redis://localhost:6379")
    result = await openConnCheck(connection_pool=connPool)
    assert result is True
