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

    @commands.command()
    @commands.has_guild_permissions(manage_guild=True)
    async def owoify(self, ctx: Context):
        """Toggles owoify in current guild."""
        current = await ctx.db.get_owoify(ctx.guild.id)
        await ctx.db.set_owoify(ctx.guild.id, not current)
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
        if prefix.startswith((f'<@!{self.bot.user.id}>', f'<@{self.bot.user.id}>')):
            await ctx.send('Mention prefixes are reserved.')
            return

        try:
            await ctx.db.add_prefix(ctx.guild.id, prefix)
        except asyncpg.UniqueViolationError:
            await ctx.send('This prefix is already in this guild.')
            return

        await ctx.send('\U0001f44c')

    @prefix.command('remove', aliases=['del', 'delete'])
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    async def prefix_remove(self, ctx: Context, prefix: str):
        """Removes a prefix from the guild."""
        prefixes = await ctx.db.get_prefixes(ctx.guild.id)
        if prefix not in prefixes:
            await ctx.send('That prefix is not in the guild\'s prefix list.')
            return

        await ctx.db.del_prefix(ctx.guild.id, prefix)
        await ctx.send('\U0001F44C')
