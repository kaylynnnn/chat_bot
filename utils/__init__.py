import asyncio
from typing import Any, Awaitable, Callable, ParamSpec, TypeVar


__all__ = ('to_thread',)


T = TypeVar('T')
P = ParamSpec('P')


def to_thread(func: Callable[P, T]) -> Callable[P, Awaitable[T]]:
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper
