import os
import sys
from pathlib import Path

import pytest
from redis.asyncio.connection import ConnectionPool

path = Path(__file__).parents[2]
packagePath = os.path.join(str(path), "Bot", "Libs")
sys.path.append(packagePath)

from utils.redis import memCache, setupRedisConnPool


@pytest.mark.asyncio
async def test_setup_redis_conn_pool():
    await setupRedisConnPool()
    connPoolCache = await memCache.get("main")
    assert isinstance(connPoolCache, ConnectionPool)  # nosec
