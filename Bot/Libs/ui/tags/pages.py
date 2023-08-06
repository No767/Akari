from typing import List, TypedDict

import discord
from Libs.utils.pages import SimplePages


class TagEntry(TypedDict):
    id: int
    name: str
    owner_id: int


class TagPageEntry:
    __slots__ = ("id", "name", "owner_id")

    def __init__(self, entry: TagEntry):
        self.id: int = entry["id"]
        self.name: str = entry["name"]
        self.owner_id: int = entry["owner_id"]

    def __str__(self) -> str:
        return f"{self.name} (ID: {self.id}, Owner: <@{self.owner_id}>)"


class TagPages(SimplePages):
    def __init__(
        self,
        entries: List[TagEntry],
        *,
        interaction: discord.Interaction,
        per_page: int = 10,
    ):
        converted = [TagPageEntry(entry) for entry in entries]
        super().__init__(converted, per_page=per_page, interaction=interaction)
