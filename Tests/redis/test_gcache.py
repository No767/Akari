import sys
from pathlib import Path

path = Path(__file__).parents[2].joinpath("Bot")
sys.path.append(str(path))

from Libs.cache import akariCPM
from redis.asyncio.connection import ConnectionPool


def test_get_cp():
    connPool = akariCPM.getConnPool()
    assert isinstance(connPool, ConnectionPool)


def test_creation_cp():
    connPool = akariCPM.createPool()
    assert isinstance(connPool, ConnectionPool)
