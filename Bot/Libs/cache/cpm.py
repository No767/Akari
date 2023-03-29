from typing import Optional

from redis.asyncio.connection import ConnectionPool


class AkariCPM:
    def __init__(
        self, host: str = "127.0.0.1", port: int = 6379, password: Optional[str] = None
    ) -> None:
        self.host = host
        self.port = port
        self.password = password
        self.connPool = None

    def createConnPool(self) -> ConnectionPool:
        self.connPool = ConnectionPool(
            host=self.host, port=self.port, password=self.password
        )
        return self.connPool

    def getConnPool(self) -> ConnectionPool:
        if not self.connPool:
            return self.createConnPool()
        return self.connPool
