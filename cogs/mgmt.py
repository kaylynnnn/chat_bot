from typing import Iterable

import asyncpg
import discord
from deps import Bot, Context
from discord.ext import commands

from models import Guild, Prefix


async def setup(bot: Bot):
    await bot.add_cog(Management(bot))


class Management(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def get_prefixes(self, guild: discord.Guild) -> list[str]:
        async with self.bot.db as conn:
            records: Iterable[asyncpg.Record] = await Prefix.fetch(conn, guild=guild.id)
        return [r['prefix'] for r in records]

    @commands.command()
    @commands.has_guild_permissions(manage_guild=True)
    async def owoify(self, ctx: Context, value: bool):
        """Enable or disable owoify in current guild."""
        async with self.bot.db as conn:
            try:
                await Guild.insert(conn, guild=ctx.guild.id, owoify=value)
            except asyncpg.UniqueViolationError:
                await Guild.update_where(conn, 'guild = $1', ctx.guild.id, owoify=value)

        await ctx.send('\U0001f44c')

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def prefix(self, ctx: Context):
        """Base command for managing prefixes."""
        prefixes = await self.bot.get_prefix(ctx.message)
        fmt = '\n'.join(f'{discord.utils.escape_markdown(p)}' for p in prefixes[1:])
        embed = discord.Embed(title=f'Prefixes for this guild', description=fmt)
        await ctx.send(embed=embed)

    @prefix.command('add')
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    async def prefix_add(self, ctx: Context, prefix: str):
        """Adds a new prefix to the guild."""
        prefixes = await self.get_prefixes(ctx.guild)  # type: ignore
        if prefix in prefixes:
            await ctx.send('This is already a prefix.')
            return

        if prefix.startswith((f'<@!{self.bot.user.id}>', f'<@{self.bot.user.id}>')):
            await ctx.send('Mention prefixes are reserved.')
            return

        async with self.bot.db as conn:
            await Prefix.insert(conn, guild=ctx.guild.id, prefix=prefix)
        
        self.bot.prefix_cache[ctx.guild.id].append(prefix)

        await ctx.send('\U0001f44c')

    @prefix.command('remove', aliases=['del', 'delete'])
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    async def prefix_remove(self, ctx: Context, prefix: str):
        """Removes a prefix from the guild."""
        prefixes = await self.get_prefixes(ctx.guild)  # type: ignore
        if prefix not in prefixes:
            await ctx.send('That prefix is not in the guild\'s prefix list.')
            return

        async with self.bot.db as conn:
            await Prefix.delete(conn, guild=ctx.guild.id, prefix=prefix)
        
        self.bot.prefix_cache[ctx.guild.id].remove(prefix)

        await ctx.send('\U0001F44C')
