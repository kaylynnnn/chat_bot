from __future__ import annotations

from typing import TYPE_CHECKING
import asyncpg
import discord

from discord.ext import commands
from models import Guild

from utils import owoify_embed, owoify_text

if TYPE_CHECKING:
    from deps import Bot

__all__ = ('Context',)


class Context(commands.Context):
    bot: Bot

    async def _check_owoify(self, guild: discord.Guild | None):
        if not guild:
            return False

        async with self.bot.db as conn:
            record: asyncpg.Record = await Guild.fetch_row(conn, guild=guild.id)

        return record['owoify']

    async def send(self, content: str | None = None, **kwargs):
        if await self._check_owoify(self.guild):
            if content:
                content = owoify_text(content)

            embed: discord.Embed | None = kwargs.pop('embed', None)
            if embed:
                embed = owoify_embed(embed)
                kwargs['embed'] = embed

        await super().send(content, **kwargs)
