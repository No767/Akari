import sys
from pathlib import Path

path = Path(__file__).parents[2].joinpath("Bot")
sys.path.append(str(path))

from redis.asyncio.connection import ConnectionPool

from Bot.Libs.utils.redis import akariCP


def test_get_cp():
    connPool = akariCP.getConnPool()
    assert isinstance(connPool, ConnectionPool)


def test_creation_cp():
    connPool = akariCP.createConnPool()
    assert isinstance(connPool, ConnectionPool)
