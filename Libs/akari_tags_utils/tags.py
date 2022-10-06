from tortoise import Tortoise
from datetime import datetime
import uuid
import asyncio
import uvloop

from . import AkariTags

class AkariTagsUtils:
    def __init__(self, uri: str, models: list):
        self.self = self
        self.uri = uri
        self.models = models
        
    async def createData(self, uuid: uuid.uuid4(), tag_name: str, tag_content: str, created_at: datetime, guild_id: int, author_id: int):
        """Creates and inserts the data into the DB

        Args:
            uuid (uuid.uuid4): Item UUID
            tag_name (str): Tag Name
            tag_content (str): Tag Content
            created_at (datetime): `datetime` for when it is created
            guild_id (int): Guild ID
            author_id (int): Author ID
        """
        await Tortoise.init(db_url=self.uri, modules={"models": self.models})
        await AkariTags.create(
            uuid=uuid,
            tag_name=tag_name,
            tag_content=tag_content,
            created_at=created_at,
            guild_id=guild_id,
            author_id=author_id
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
        data = await AkariTags.all().values()
        await Tortoise.close_connections()
        return data
    
    async def getAllData(self, guild_id: int) -> list:
        """Gets all of the data from the DB w/ the guild id

        Args:
            guild_id (int): Discord Guild ID

        Returns:
            list: A list of the data
        """
        await Tortoise.init(db_url=self.uri, modules={"models": self.models})
        data = await AkariTags.filter(guild_id=guild_id).all().values()
        await Tortoise.close_connections()
        return data
    
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    
    async def purgeData(self, guild_id: int) -> None:
        """Completely purges the tags that a guild has

        Args:
            guild_id (int): Discord Guild ID
        """
        await Tortoise.init(db_url=self.uri, modules={"models": self.models})
        await AkariTags.filter(guild_id=guild_id).all().delete()
        await Tortoise.close_connections()
        
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    
    async def removeTag(self, name: str, guild_id: int) -> None:
        """Removes a tag from the DB

        Args:
            name (str): Tag Name
            guild_id (int): Discord Guild ID
        """
        await Tortoise.init(db_url=self.uri, modules={"models": self.models})
        await AkariTags.filter(tag_name=name, guild_id=guild_id).all().delete()
        await Tortoise.close_connections()
        
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())