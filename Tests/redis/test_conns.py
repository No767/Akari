import sys
from pathlib import Path

import pytest

path = Path(__file__).parents[2].joinpath("Bot")
sys.path.append(str(path))

from Libs.cache import AkariCPM
from Libs.utils.redis import pingRedisServer


@pytest.mark.asyncio
async def test_ping_redis():
    cpm = AkariCPM()
    connPool = cpm.getConnPool()
    res = await pingRedisServer(connection_pool=connPool)

    assert res is True


# testing this will take too long
# Literally it's a recursive call
# @pytest.mark.asyncio
# async def test_redis_check():
#    res = await redisCheck()
#    assert res is True
