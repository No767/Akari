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