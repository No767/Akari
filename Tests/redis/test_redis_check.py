import os
import sys
from pathlib import Path

import pytest
from redis.asyncio.connection import ConnectionPool

path = Path(__file__).parents[2]
packagePath = os.path.join(str(path), "Bot", "Libs")
sys.path.append(packagePath)

from utils.redis import pingRedisServer


@pytest.mark.asyncio
async def test_redis_ping():
    connPool = ConnectionPool(max_connections=25).from_url("redis://localhost:6379")
    isServerUp = await pingRedisServer(connection_pool=connPool)
    assert isServerUp is True  # nosec
