import asyncio
import uuid
from datetime import datetime

import uvloop
from tortoise import Tortoise

from . import AkariAdminLogs


class AkariAdminLogsUtils:
    def __init__(self, uri: str, models: list):
        """Constructor for the `AkariAdminLogsUtils` class

        Args:
            uri (str): The connection URI
            models (list): A list of the models
        """
        self.self = self
        self.uri = uri
        self.models = models

    async def addALRow(
        self,
        uuid: uuid.uuid4(),
        guild_id: int,
        action_username: str,
        affected_username: str,
        type_of_action: str,
        reason: str,
        date_issued: datetime,
        duration: int,
    ) -> None:
        """Adds a new row into the Admin Logs

        This will probably get commonly used a lot...

        Args:
            uuid (uuid.uuid4): UUID Item
            guild_id (int): Discord Guild ID
            action_username (str): Username of the person who issued the action
            affected_username (str): Username of the person who was affected by the action
            type_of_action (str): Type of action (e.g. timeout, ban, kick, etc.)
            reason (str): Reason for the action
            date_issued (datetime): Date the action was issued
            duration (int): Duration of the action (in seconds)
        """
        await Tortoise.init(db_url=self.uri, modules={"models": self.models})
        await AkariAdminLogs.create(
            uuid=uuid,
            guild_id=guild_id,
            action_username=action_username,
            affected_username=affected_username,
            type_of_action=type_of_action,
            reason=reason,
            date_issued=date_issued,
            duration=duration,
        )
        await Tortoise.close_connections()

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    async def getAllRows(self) -> list:
        """Gets all of the rows from the DB.

        This should only be really used in testing

        Returns:
            list: A list of the data
        """
        await Tortoise.init(db_url=self.uri, modules={"models": self.models})
        returnData = await AkariAdminLogs.all().values()
        await Tortoise.close_connections()
        return returnData

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    async def getAllALData(self, guild_id: int) -> list:
        """Gets all of the admin logs for that guild

        Args:
            guild_id (int): Discord Guild ID

        Returns:
            list: A list containing dicts that have the data
        """
        await Tortoise.init(db_url=self.uri, modules={"models": self.models})
        data = await AkariAdminLogs.filter(guild_id=guild_id).all().values()
        await Tortoise.close_connections()
        return data

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    async def getLogsFiltered(self, guild_id: int, type_of_action: str) -> list:
        """Gets any logs but filtered

        Args:
            guild_id (int): Discord Guild ID
            type_of_action (str): Type of action (eg ban, kick, etc)

        Returns:
            list: A list containing dicts that have the data
        """
        await Tortoise.init(db_url=self.uri, modules={"models": self.models})
        data = (
            await AkariAdminLogs.filter(
                guild_id=guild_id, type_of_action=type_of_action
            )
            .all()
            .values()
        )
        await Tortoise.close_connections()
        return data

    async def purgeAllALData(self, guild_id: int) -> None:
        """Completely purges that server of any admin logs

        Args:
            guild_id (int): Discord Guild ID
        """
        await Tortoise.init(db_url=self.uri, modules={"models": self.models})
        await AkariAdminLogs.filter(guild_id=guild_id).all().delete()
        await Tortoise.close_connections()

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
