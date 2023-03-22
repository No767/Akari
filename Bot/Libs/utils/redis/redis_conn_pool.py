from typing import Optional

from redis.asyncio.connection import Connection, ConnectionPool


class RedisConnPool:
    def __init__(
        self, host: str = "127.0.0.1", port: int = 6379, password: Optional[str] = None
    ) -> None:
        self.host = host
        self.port = port
        self.password = password
        self.connPool = None

    def createConnPool(self) -> ConnectionPool:
        conn = Connection(host=self.host, port=self.port, password=self.password)
        self.connPool = ConnectionPool(connection_class=conn)  # type: ignore
        return self.connPool

    def getConnPool(self) -> ConnectionPool:
        if not self.connPool:
            return self.createConnPool()
        return self.connPool
