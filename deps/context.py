from typing import Generic, TypeVar

from discord.ext import commands

__all__ = ('Context',)


BotT = TypeVar('BotT', bound=commands.Bot | commands.AutoShardedBot, covariant=True)


class Context(commands.Context, Generic[BotT]):
    pass
