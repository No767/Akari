import os
from pathlib import Path

from dotenv import load_dotenv

from .redis_conn_pool import RedisConnPool

path = Path(__file__).parents[3].joinpath(".env")
load_dotenv(dotenv_path=path)

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

akariCP: RedisConnPool = RedisConnPool(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)  # type: ignore
