import os
import sys
from pathlib import Path

path = Path(__file__).parents[2].joinpath("Bot")
sys.path.append(str(path))

from Libs.cache import AkariCPM
from redis.asyncio.connection import ConnectionPool

REDIS_URI = os.environ["REDIS_URI"]


def test_get_conn():
    cpm = AkariCPM(uri=REDIS_URI)
    assert isinstance(cpm.getConnPool(), ConnectionPool)


def test_create_conn():
    cpm = AkariCPM(uri=REDIS_URI)
    assert isinstance(cpm.createPool(), ConnectionPool)


def test_create_get_conn():
    cpm = AkariCPM(uri=REDIS_URI)
    cpm.createPool()
    assert isinstance(cpm.getConnPool(), ConnectionPool)
