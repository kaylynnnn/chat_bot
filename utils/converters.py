from lib2to3.pytree import convert

import discord
from deps import Context
from discord.ext import commands


__all__ = ('RoleConverter',)


class RoleConverter(commands.Converter[discord.Role]):
    async def convert(self, ctx: Context, argument: str):
        try:
            return await commands.RoleConverter().convert(ctx, argument)
        except commands.RoleNotFound:
            role = discord.utils.find(
                lambda r: r.name.lower() == argument.lower(),
                ctx.guild.roles,
            )
            if role is None:
                raise commands.RoleNotFound(argument)
            return role
