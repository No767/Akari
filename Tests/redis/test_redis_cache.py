import json
import os
import sys
import uuid
from pathlib import Path

import pytest
from aiocache import Cache
from redis.asyncio.connection import ConnectionPool

path = Path(__file__).parents[2]
packagePath = os.path.join(str(path), "Bot", "Libs")
sys.path.append(packagePath)

from cache import AkariCache, CommandKeyBuilder

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
    await cache.setBasicCommandCache(key=key, value=DATA)
    res = await cache.getBasicCommandCache(key=key)
    assert (res == DATA) and (isinstance(res, str))  # nosec


@pytest.mark.asyncio
async def test_basic_cache_from_mem():
    key = CommandKeyBuilder(id=None, command=None)
    connPool = ConnectionPool().from_url("redis://localhost:6379/0")
    memCache = Cache(Cache.MEMORY)
    await memCache.set("redis_conn_pool", connPool)
    getConnPool = await memCache.get("redis_conn_pool")
    if getConnPool is None:
        raise ValueError("Unable to get conn pool from mem cache")
    cache = AkariCache(connection_pool=getConnPool)
    res = await cache.getBasicCommandCache(key=key)
    assert (res == DATA) and (isinstance(res, str))  # nosec


@pytest.mark.asyncio
async def test_json_cache(load_json_data):
    key: str = CommandKeyBuilder(id=str(uuid.uuid4()), command="test")
    connPool = ConnectionPool().from_url("redis://localhost:6379/0")
    cache = AkariCache(connection_pool=connPool)
    await cache.setJSONCache(key=key, value=load_json_data, ttl=60)
    res = await cache.getJSONCache(key=key)
    assert (res == load_json_data) and (isinstance(res, dict))  # nosec


@pytest.mark.asyncio
async def test_json_cache_mem(load_json_data):
    key = CommandKeyBuilder(id=str(uuid.uuid4()), command="test test")
    memCache = Cache(Cache.MEMORY)
    connPool = ConnectionPool().from_url("redis://localhost:6379/0")
    await memCache.add(key="redis_conn_pool", value=connPool)
    connPool = await memCache.get("redis_conn_pool")
    if connPool is None:
        raise ValueError("Unable to get conn pool from mem cache")
    cache = AkariCache(connection_pool=connPool)
    await cache.setJSONCache(key=key, value=load_json_data, ttl=60)
    res = await cache.getJSONCache(key=key)
    assert (res == load_json_data) and (isinstance(res, dict))  # nosec
