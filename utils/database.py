import asyncio
from typing import Iterable
import asyncpg
from donphan import MaybeAcquire
from models import Guild, Prefix


__all__ = ('Database',)


class Database:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self.pool = pool
        self.acquire_conn = MaybeAcquire(pool=self.pool)
        asyncio.create_task(self._setup())

    async def _setup(self):
        async with self.acquire_conn as conn:
            await Prefix.create(conn, if_not_exists=True)
            await Guild.create(conn, if_not_exists=True)
    
    async def close(self) -> None:
        await self.pool.close()

    async def get_prefixes(self, guild_id: int) -> list[str]:
        async with self.acquire_conn as conn:
            records: Iterable[asyncpg.Record] = await Prefix.fetch(conn, guild=guild_id)
        
        return [record['prefix'] for record in records]

    async def get_owoify(self, guild_id: int) -> bool:
        async with self.acquire_conn as conn:
            record: asyncpg.Record = await Guild.fetch_row(conn, guild=guild_id)
        
        return record['owoify'] or False

    async def add_prefix(self, guild_id: int, prefix: str) -> None:
        async with self.acquire_conn as conn:
            await Prefix.insert(conn, guild=guild_id, prefix=prefix)

    async def del_prefix(self, guild_id: int, prefix: str) -> None:
        async with self.acquire_conn as conn:
            await Prefix.delete(conn, guild=guild_id, prefix=prefix)

    async def set_owoify(self, guild_id: int, value: bool) -> None:
        async with self.acquire_conn as conn:
            try:
                await Guild.insert(conn, guild=guild_id, owoify=value)
            except asyncpg.UniqueViolationError:
                await Guild.update_where(conn, 'guild = $1', guild_id, owoify=value)
