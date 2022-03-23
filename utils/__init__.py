import asyncio
from typing import Awaitable, Callable, ParamSpec, TypeVar

from .converters import *
from .owoify import *


__all__ = ('to_thread', 'RoleConverter', 'owoify_text', 'owoify_embed',)


T = TypeVar('T')
P = ParamSpec('P')


def to_thread(func: Callable[P, T]) -> Callable[P, Awaitable[T]]:
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper
