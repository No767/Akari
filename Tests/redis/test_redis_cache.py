import json
import sys
import uuid
from pathlib import Path

import pytest
from redis.asyncio.connection import ConnectionPool

path = Path(__file__).parents[2].joinpath("Bot")
sys.path.append(str(path))

from Libs.cache import AkariCache, AkariCPM, CommandKeyBuilder

DATA = "Hello World"


@pytest.fixture(autouse=True)
def load_json_data():
    fileDir = Path(__file__).parent.joinpath("data")
    with open(fileDir.joinpath("redis_test.json"), "r") as f:
        data = json.load(f)
        return data


@pytest.mark.asyncio
async def test_basic_cache():
    key = CommandKeyBuilder(id=None, command=None)
    connPool = ConnectionPool().from_url("redis://localhost:6379/0")
    cache = AkariCache(connection_pool=connPool)
    await cache.setBasicCache(key=key, value=DATA)
    res = await cache.getBasicCache(key=key)
    assert (res == DATA.encode("utf-8")) and (isinstance(res, bytes))  # nosec


@pytest.mark.asyncio
async def test_basic_cache_from_mem():
    key = CommandKeyBuilder(id=None, command=None)
    cpm = AkariCPM(uri="redis://localhost:6379/0")
    getConnPool = cpm.getConnPool()
    cache = AkariCache(connection_pool=getConnPool)
    res = await cache.getBasicCache(key=key)
    assert (res == DATA) and (isinstance(res, str))  # nosec


@pytest.mark.asyncio
async def test_json_cache(load_json_data):
    key: str = CommandKeyBuilder(id=uuid.uuid4(), command="test")
    connPool = ConnectionPool().from_url("redis://localhost:6379/0")
    cache = AkariCache(connection_pool=connPool)
    await cache.setJSONCache(key=key, value=load_json_data, ttl=60)
    res = await cache.getJSONCache(key=key)
    assert (res == load_json_data) and (isinstance(res, dict))  # nosec


@pytest.mark.asyncio
async def test_json_cache_mem(load_json_data):
    key = CommandKeyBuilder(id=uuid.uuid4(), command="test test")
    cpm = AkariCPM(uri="redis://localhost:6379/0")
    connPool = cpm.getConnPool()
    cache = AkariCache(connection_pool=connPool)
    await cache.setJSONCache(key=key, value=load_json_data, ttl=60)
    res = await cache.getJSONCache(key=key)
    assert (res == load_json_data) and (isinstance(res, dict))  # nosec


@pytest.mark.asyncio
async def test_cache_exists():
    key = CommandKeyBuilder(id=1275, command="more testing")
    connPool = ConnectionPool().from_url("redis://localhost:6379/0")
    cache = AkariCache(connection_pool=connPool)
    await cache.setBasicCache(key=key, value=DATA)
    assert (await cache.cacheExists(key=key)) is True  # nosec


@pytest.mark.asyncio
async def test_default_key_builder():
    connPool = ConnectionPool.from_url("redis://localhost:6379/0")
    cache = AkariCache(connection_pool=connPool)
    await cache.setBasicCache(key=None, value=DATA)
    res = await cache.getBasicCache(key=f"cache:akari:None:None")
    assert res == DATA.encode("utf-8") and isinstance(res, bytes)  # nosec


@pytest.mark.asyncio
async def test_default_key_builder_json(load_json_data):
    connPool = ConnectionPool.from_url("redis://localhost:6379/0")
    cache = AkariCache(connection_pool=connPool)
    await cache.setJSONCache(key="no", value=load_json_data)
    res = await cache.getJSONCache(key="nope")
    assert res is None  # nosec
