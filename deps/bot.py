from __future__ import annotations

import os
import pathlib
from typing import Iterable

import aiohttp
import asyncpg
import discord
import donphan
from discord.ext import commands
from donphan import MaybeAcquire

from .context import Context
from models import Guild, Prefix

os.environ['JISHAKU_NO_UNDERSCORE'] = 'True'
os.environ['JISHAKU_NO_DM_TRACEBACK'] = 'True'
os.environ['JISHAKU_HIDE'] = 'True'

EXTENSIONS: list[str] = ['jishaku']

cogs_path = pathlib.Path("./cogs")
COGS = [f'cogs.{x.name[:-3]}' for x in cogs_path.glob("[!_]*.py")]
EXTENSIONS.extend(COGS)

INTENTS = discord.Intents.default()
INTENTS.members = True
INTENTS.message_content = True


async def get_prefix(bot: Bot, message: discord.Message) -> list[str]:
    if not message.guild:
        return commands.when_mentioned_or('?')(bot, message)

    ret: list[str] = bot.prefix_cache.get(message.guild.id, [])
    if not ret:
        async with bot.db as conn:
            records: Iterable[asyncpg.Record] = await Prefix.fetch(conn, guild=message.guild.id)

        ret: list[str] = [r['prefix'] for r in records]
        bot.prefix_cache[message.guild.id] = ret
        if not ret:
            ret.append('gh+')

    return commands.when_mentioned_or(*ret)(bot, message)


class HelpCommand(commands.MinimalHelpCommand):
    async def get_destination(self) -> discord.abc.Messageable:
        return self.context


class Bot(commands.Bot):
    session: aiohttp.ClientSession
    pool: asyncpg.Pool
    db: MaybeAcquire

    def __init__(self, *, config: dict[str, str]):
        super().__init__(
            command_prefix=get_prefix,
            intents=INTENTS,
            owner_ids={671777334906454026, 766953372309127168},
            help_command=HelpCommand()
        )
        self.config = config
        self._once_ready = False
        self.event(self.on_once_ready)
        self.prefix_cache: dict[int, list[str]] = {}

    async def setup_hook(self):
        for extension in EXTENSIONS:
            try:
                await self.load_extension(extension)
                print(f'Loaded {extension}')
            except Exception as err:
                print(f'Error loading {extension} - {err.__class__.__name__}: {err}')

        self.pool = await donphan.create_pool(self.config['database_dsn'])
        self.db = MaybeAcquire(pool=self.pool)
        self.session = aiohttp.ClientSession()

        async with self.db as conn:
            await Prefix.create(conn, if_not_exists=True)
            await Guild.create(conn, if_not_exists=True)

    async def on_once_ready(self):
        await self.change_presence(
            activity=discord.Game('this bot sucks'),
            status=discord.Status.dnd,
        )

    async def on_ready(self):
        if not self._once_ready:
            self.dispatch('once_ready')
            self._once_ready = True

        print(f'Ready! Logged in as {self.user} ({self.user.id})')

    async def get_context(self, message: discord.Message, *, cls=Context):
        return await super().get_context(message, cls=cls)

    def run(self, token: str | None = None, *, reconnect: bool = True) -> None:
        super().run(token or self.config['token'], reconnect=reconnect)

    async def close(self):
        await self.pool.close()
        await self.session.close()
        await super().close()
