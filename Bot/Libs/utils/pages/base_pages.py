import discord

from .paginator import AkariPages
from .sources import SimplePageSource


class SimplePages(AkariPages):
    """A simple pagination session reminiscent of the old Pages interface.

    Basically an embed with some normal formatting.
    """

    def __init__(
        self, entries, *, interaction: discord.Interaction, per_page: int = 12
    ):
        super().__init__(
            SimplePageSource(entries, per_page=per_page), interaction=interaction
        )
        self.embed = discord.Embed(colour=discord.Colour.from_rgb(200, 168, 255))
