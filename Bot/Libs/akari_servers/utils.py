import asyncio

import uvloop
from akari_utils import AkariCM

from .models import AkariServers


class AkariServerUtils:
    """Utils to help with adding the server profile into the DB"""

    def __init__(self, uri: str, models: list) -> None:
        """Constructor for the `AkariServerUtils` class

        Args:
            uri (str): Connection URI
            models (list): List of Tortoise ORM models
        """
        self.self = self
        self.uri = uri
        self.models = models

    async def addDefaultProfile(self, guild_id: int) -> None:
        """Adds the server into the DB with the "default" profile

        The default profile is this:
        - Admin Logs: True
        - ModMail: False
        - Suggestions: False
        - Tags: True

        Args:
            guild_id (int): The Discord Guild ID
        """
        async with AkariCM(uri=self.uri, models=self.models):
            await AkariServers(
                guild_id=guild_id,
                admin_logs=True,
                modmail=False,
                suggestions=False,
                tags=True,
            ).save()

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
