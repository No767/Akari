import asyncpg
import logging

async def ensureOpenConn(conn_pool: asyncpg.Pool) -> bool:
    """Ensures that the current connection pulled from the pool can be run.
    
    Args:
        conn_pool (asyncpg.Pool): The connection pool to get connections from.
    
    Returns:
        bool: True if the connection can be ran.
    """
    logger = logging.getLogger("discord")
    async with conn_pool.acquire() as conn:
        connStatus = conn.is_closed()
        if connStatus is False:
            logger.info("Successfully connected to PostgreSQL")
            return True
    logger.error("Failed to connect to PostgreSQL")
    return False
