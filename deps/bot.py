from __future__ import annotations

import os
import pathlib
from typing import Iterable

import aiohttp
import aioredis
import asyncpg
import discord
import donphan
from discord.ext import commands
from donphan import MaybeAcquire

from utils import Database

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

    ret: list[str] = await bot.db.get_prefixes(message.guild.id)
    return commands.when_mentioned_or(*ret)(bot, message)


class HelpCommand(commands.MinimalHelpCommand):
    def get_destination(self) -> discord.abc.Messageable:
        return self.context


class Bot(commands.Bot):
    session: aiohttp.ClientSession
    pool: asyncpg.Pool
    db: Database
    _kal_av_hash: int

    def __init__(self, *, config: dict[str, str | list[str | int]]):
        super().__init__(
            command_prefix=get_prefix,
            intents=INTENTS,
            owner_ids=set(config['owner_ids']),
            help_command=HelpCommand(),
        )
        self.config = config
        self._once_ready = False
        self.event(self.on_once_ready)

    async def setup_hook(self):
        for extension in EXTENSIONS:
            try:
                await self.load_extension(extension)
                print(f'Loaded {extension}')
            except Exception as err:
                print(f'Error loading {extension} - {err.__class__.__name__}: {err}')

        self.pool = await donphan.create_pool(self.config['database_dsn'])  # type: ignore
        redis = await aioredis.from_url(self.config['redis_dsn'], decode_responses=True)
        self.db = Database(self.pool, redis)
        self.session = aiohttp.ClientSession()

    async def try_user(self, user: int) -> discord.User:
        return self.get_user(user) or await self.fetch_user(user)

    @property
    async def kal(self) -> discord.User:
        return await self.try_user(671777334906454026)

    async def on_once_ready(self):
        await self.change_presence(
            activity=discord.Game('this bot sucks'),
            status=discord.Status.dnd,
        )
        self._kal_av_hash = hash((await self.kal).avatar)

    async def on_ready(self):
        if not self._once_ready:
            self.dispatch('once_ready')
            self._once_ready = True

        print(f'Ready! Logged in as {self.user} ({self.user.id})')

    async def get_context(self, message: discord.Message, *, cls=Context):
        return await super().get_context(message, cls=cls)

    async def start(self, token: str | None = None, *, reconnect: bool = True) -> None:
        await super().start(token or self.config['token'], reconnect=reconnect)  # type: ignore

    async def close(self):
        await self.db.close()
        await self.session.close()
        await super().close()
