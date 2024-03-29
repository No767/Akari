from __future__ import annotations

from typing import Any, Dict, List

import discord
from discord.ext import menus
from discord.ext.commands import Paginator as CommandPaginator

from ..embeds import Embed
from .paginator import AkariPages


class BasicListSource(menus.ListPageSource):
    """Basic list source for the paginator"""

    async def format_page(self, menu: AkariPages, entries: List[Any]) -> Embed:
        """Formats the given page

        Args:
            menu (menus.Menu): What menu should be formatted
            entries (List[Any]): List of all of the entries

        Returns:
            Embed: An embed with the formatted entries
        """
        embed = Embed(
            description=f"This is number {entries}.", color=discord.Colour.random()
        )
        return embed


class FieldPageSource(menus.ListPageSource):
    """A page source that requires (field_name, field_value) tuple items."""

    def __init__(
        self,
        entries: list[tuple[Any, Any]],
        *,
        per_page: int = 5,
        inline: bool = False,
        clear_description: bool = True,
        title: str = "",
        description: str = "",
    ) -> None:
        super().__init__(entries, per_page=per_page)
        self.embed: Embed = Embed(title=title, description=description)
        self.clear_description: bool = clear_description
        self.inline: bool = inline

    async def format_page(
        self, menu: AkariPages, entries: list[tuple[Any, Any]]
    ) -> discord.Embed:
        self.embed.clear_fields()
        if self.clear_description:
            self.embed.description = None

        for key, value in entries:
            self.embed.add_field(name=key, value=value, inline=self.inline)

        maximum = self.get_max_pages()
        if maximum > 1:
            text = (
                f"Page {menu.current_page + 1}/{maximum} ({len(self.entries)} entries)"
            )
            self.embed.set_footer(text=text)

        return self.embed


class TextPageSource(menus.ListPageSource):
    """A text based source for the paginator"""

    def __init__(self, text, *, prefix="```", suffix="```", max_size=2000):
        pages = CommandPaginator(prefix=prefix, suffix=suffix, max_size=max_size - 200)
        for line in text.split("\n"):
            pages.add_line(line)

        super().__init__(entries=pages.pages, per_page=1)

    async def format_page(self, menu: AkariPages, content: str):
        """Formats the given page

        Args:
            menu (AkariPages): Default menu passed in
            content (str): Content to format
        """
        maximum = self.get_max_pages()
        if maximum > 1:
            return f"{content}\nPage {menu.current_page + 1}/{maximum}"
        return content


class EmbedListSource(menus.ListPageSource):
    """Source for taking contents of an Embed, and formatting them into a page"""

    async def format_page(
        self, menu: AkariPages, entries: Dict[str, Any]
    ) -> discord.Embed:
        """Formatter for the embed list source

        Ideally the structure of the entries should be:
        {
            "title": "Title of the embed",
            "description": "Description of the embed",
            "image": "Image of the embed",
            "thumbnail": "Thumbnail of the embed",
            [
                {
                    "name": "Name of the embed",
                    "value": "Value of the embed",
                    "inline": True
                },
                {
                    "name": "Name of the embed",
                    "value": "Value of the embed",
                    "inline": True
                }
            ]
        }

        Args:
            menu (menus.Menu): What menu should be formatted
            entries (Dict[str, Any]) List of all of the entries to format

        Returns:
            discord.Embed: An embed with the formatted entries
        """
        maximum = self.get_max_pages()
        embed = Embed()
        embed.title = entries["title"] if "title" in entries else ""
        embed.description = entries["description"] if "description" in entries else ""
        embed.set_image(url=entries["image"]) if "image" in entries else ...
        embed.set_thumbnail(url=entries["thumbnail"]) if "thumbnail" in entries else ...
        embed.set_footer(text=f"Page {menu.current_page + 1}/{maximum}")
        if "fields" in entries:
            for item in entries["fields"]:
                embed.add_field(name=item["name"] or ..., value=item["value"] or ...)
        return embed


class SimplePageSource(menus.ListPageSource):
    async def format_page(self, menu, entries):
        pages = []
        for index, entry in enumerate(entries, start=menu.current_page * self.per_page):
            pages.append(f"{index + 1}. {entry}")

        maximum = self.get_max_pages()
        if maximum > 1:
            footer = (
                f"Page {menu.current_page + 1}/{maximum} ({len(self.entries)} entries)"
            )
            menu.embed.set_footer(text=footer)

        menu.embed.description = "\n".join(pages)
        return menu.embed
