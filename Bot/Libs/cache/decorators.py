import uuid
from functools import wraps
from typing import Any, Callable, Optional, Union

from redis.asyncio.connection import ConnectionPool

from .redis_cache import AkariCache, CommandKeyBuilder


class cache:
    """A decorator to cache the result of a function that returns a `str` to Redis.

    The function that this decorator wraps expects two args: `id: int` and `redis_pool: redis.asyncio.connection.ConnectionPool`
    **Note**: The return type of the coroutine used has to be `str` or `bytes`

    Args:
        ttl (int, optional): TTL (Time-To-Live). Defaults to 30.
    """

    def __init__(self, key: Optional[str] = None, ttl: int = 30):
        self.key = key
        self.ttl = ttl

    def __call__(self, func: Callable, *args: Any, **kwargs: Any):
        @wraps(func)
        async def wrapper(
            id: int, redis_pool: ConnectionPool, *args: Any, **kwargs: Any
        ):
            return await self.deco(func, id, redis_pool, *args, **kwargs)

        return wrapper

    async def deco(
        self,
        func: Callable,
        id: Union[int, None],
        redis_pool: ConnectionPool,
        *args,
        **kwargs
    ):
        res = await func(id, redis_pool, *args, **kwargs)
        if res is None:
            return None
        aCache = AkariCache(connection_pool=redis_pool)
        key = CommandKeyBuilder(
            prefix="cache",
            namespace="akari",
            id=id
            if id is not None
            else (self.key if self.key is not None else uuid.uuid4()),
            command=func.__name__,
        )

        if await aCache.cacheExists(key=key) is False:
            await aCache.setBasicCache(key=key, value=res, ttl=self.ttl)
            return res
        return await aCache.getBasicCache(key=key)


class cacheJson:
    """
    A decorator to cache the result of a function that returns a `dict` to Redis.

    The function that this decorator wraps expects two args: `id: int` and `redis_pool: redis.asyncio.connection.ConnectionPool`
    **Note**: The return type of the coroutine used has to be `dict`

    Args:
        redis_pool (ConnectionPool): Redis connection pool to use
        ttl (int, optional): TTL (Time-To-Live).
        Defaults to 30.
    """

    def __init__(self, key: Optional[str] = None, ttl: int = 30):
        self.key = key
        self.ttl = ttl

    def __call__(self, func: Callable, *args: Any, **kwargs: Any):
        @wraps(func)
        async def wrapper(
            id: int, redis_pool: ConnectionPool, *args: Any, **kwargs: Any
        ):
            return await self.deco(func, id, redis_pool, *args, **kwargs)

        return wrapper

    async def deco(
        self,
        func: Callable,
        id: Union[int, None],
        redis_pool: ConnectionPool,
        *args,
        **kwargs
    ):
        res = await func(id, redis_pool, *args, **kwargs)
        if res is None:
            return None
        cache = AkariCache(connection_pool=redis_pool)
        key = CommandKeyBuilder(
            prefix="cache",
            namespace="akari",
            id=id
            if id is not None
            else (self.key if self.key is not None else uuid.uuid4()),
            command=func.__name__,
        )

        if await cache.cacheExists(key=key) is False:
            await cache.setJSONCache(key=key, value=res, ttl=self.ttl)
            return res
        return await cache.getJSONCache(key=key)
