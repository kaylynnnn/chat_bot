from __future__ import annotations

from typing import TYPE_CHECKING
from discord.ext import commands

if TYPE_CHECKING:
    from deps import Bot

__all__ = ('Context',)


class Context(commands.Context):
    bot: Bot
