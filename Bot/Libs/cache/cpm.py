from typing import Optional

from redis.asyncio.connection import ConnectionPool
from yarl import URL


class AkariCPM:
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 6379,
        password: Optional[str] = None,
        uri: Optional[str] = None,
    ) -> None:
        self.host = host
        self.port = port
        self.password = password
        self.uri = uri
        self.connPool = None

    def createConnPool(self) -> ConnectionPool:
        if self.uri is not None:
            redisURI = URL(self.uri)
            completeURI = redisURI % {"decode_responses": "True"}
            self.connPool = ConnectionPool().from_url(str(completeURI))
            return self.connPool
        self.connPool = ConnectionPool(
            host=self.host,
            port=self.port,
            password=self.password,
            decode_responses=True,
        )
        return self.connPool

    def getConnPool(self) -> ConnectionPool:
        if not self.connPool:
            return self.createConnPool()
        return self.connPool
