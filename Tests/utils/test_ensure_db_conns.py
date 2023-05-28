import os
import sys
from pathlib import Path

import asyncpg
import pytest

path = Path(__file__).parents[2]
sys.path.append(str(path))


from Libs.utils import ensureOpenConn


@pytest.fixture(scope="session")
def getURI():
    uri = os.getenv("DATABASE_URL")
    if uri is None:
        return "postgresql://postgres:postgres@localhost:5432/postgres"
    return uri


@pytest.mark.asyncio
async def test_ensure_open_conns(getURI):
    async with asyncpg.create_pool(getURI) as pool:
        res = await ensureOpenConn(pool)
        assert res is True
