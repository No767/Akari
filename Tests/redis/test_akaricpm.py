import sys
from pathlib import Path

path = Path(__file__).parents[2].joinpath("Bot")
sys.path.append(str(path))

from Libs.cache import AkariCPM
from redis.asyncio.connection import ConnectionPool


def test_get_conn():
    cpm = AkariCPM()
    assert isinstance(cpm.getConnPool(), ConnectionPool)


def test_create_conn():
    cpm = AkariCPM()
    assert isinstance(cpm.createConnPool(), ConnectionPool)


def test_create_get_conn():
    cpm = AkariCPM()
    cpm.createConnPool()
    assert isinstance(cpm.getConnPool(), ConnectionPool)
