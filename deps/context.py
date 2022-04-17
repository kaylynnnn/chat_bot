from __future__ import annotations

from typing import TYPE_CHECKING
import discord

from discord.ext import commands

from utils import owoify_embed, owoify_text

if TYPE_CHECKING:
    from deps import Bot

__all__ = ('Context',)


class Context(commands.Context):
    bot: Bot

    @property
    def db(self):
        return self.bot.db

    async def _check_owoify(self, guild: discord.Guild | None) -> bool:
        if not guild:
            return False

        return await self.bot.db.get_owoify(self.guild.id)

    async def send(
        self, content: str | None = None, dont_owo: bool = False, **kwargs
    ) -> discord.Message:
        if not dont_owo and await self._check_owoify(self.guild):
            content = owoify_text(content) if content else None

            embed: discord.Embed | None = kwargs.pop('embed', None)
            if embed:
                embed = owoify_embed(embed)
                kwargs['embed'] = embed

        return await super().send(content, **kwargs)
