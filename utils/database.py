import asyncio
import aioredis
import asyncpg
from donphan import MaybeAcquire
from models import Guild, Prefix


__all__ = ('Database',)


class Database:
    def __init__(self, pool: asyncpg.Pool, redis: aioredis.Redis) -> None:
        self.pool = pool
        self.redis = redis
        self.acquire_conn = MaybeAcquire(pool=self.pool)
        asyncio.create_task(self._setup())

    async def _setup(self):
        async with self.acquire_conn as conn:
            await Prefix.create(conn, if_not_exists=True)
            await Guild.create(conn, if_not_exists=True)

    async def close(self) -> None:
        await self.pool.close()
        await self.redis.close()

    async def get_prefixes(self, guild_id: int) -> list[str]:
        cached = await self.redis.lrange(f'{guild_id}:prefix', 0, -1)
        if not cached:
            async with self.acquire_conn as conn:
                records = await Prefix.fetch(conn, guild=guild_id)
            ret = [rec['prefix'] for rec in records]
            await self.redis.lpush(f'{guild_id}:prefix', *ret or 'gh+')
        else:
            ret = [el for el in cached]
        return ret

    async def get_owoify(self, guild_id: int) -> bool:
        ret = await self.redis.get(f'{guild_id}:owoify')
        return bool(int(ret))

    async def add_prefix(self, guild_id: int, prefix: str) -> None:
        async with self.acquire_conn as conn:
            await Prefix.insert(
                conn, guild=guild_id, prefix=prefix
            )
        await self.redis.lpush(f'{guild_id}:prefix', prefix)

    async def del_prefix(self, guild_id: int, prefix: str) -> None:
        async with self.acquire_conn as conn:
            await Prefix.delete(conn, guild=guild_id, prefix=prefix)
        await self.redis.lrem(f'{guild_id}:prefix', 0, prefix)

    async def set_owoify(self, guild_id: int, value: bool) -> None:
        async with self.acquire_conn as conn:
            await Guild.insert(
                conn,
                guild=guild_id,
                update_on_conflict=(Guild.guild,),
                owoify=value
            )
        await self.redis.set(f'{guild_id}:owoify', int(value))
