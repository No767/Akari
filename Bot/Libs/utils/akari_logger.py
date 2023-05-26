import logging
from types import TracebackType
from typing import Optional, Type, TypeVar

import discord

BE = TypeVar("BE", bound=BaseException)


class AkariLogger:
    def __init__(self) -> None:
        self.self = self
        self.log = logging.getLogger("discord")

    def __enter__(self) -> None:
        fmt = logging.Formatter(
            fmt="%(asctime)s %(levelname)s    %(message)s",
            datefmt="[%Y-%m-%d %H:%M:%S]",
        )
        discord.utils.setup_logging(formatter=fmt)

    def __exit__(
        self,
        exc_type: Optional[Type[BE]],
        exc: Optional[BE],
        traceback: Optional[TracebackType],
    ) -> None:
        self.log.info("Shutting down Akari...")
