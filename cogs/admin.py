import asyncio
import json
import os
from typing import NamedTuple, cast

import discord

from deps import Bot, Context
from discord.ext import commands, tasks
from jishaku.codeblocks import codeblock_converter


async def run_shell(cmd: str) -> str:
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, _ = await proc.communicate()

    return stdout.decode()


class Codeblock(NamedTuple):
    language: str
    content: str


class CodeblockConverter(commands.Converter[Codeblock]):
    async def convert(self, ctx: Context[Bot], argument: str) -> Codeblock:
        result = codeblock_converter(argument)
        return Codeblock(result.language, result.content)


async def setup(bot: Bot):
    await bot.add_cog(Admin(bot))


class Admin(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def cog_check(self, ctx: Context[Bot]) -> bool:
        check = await self.bot.is_owner(ctx.author)
        if not check:
            raise commands.NotOwner
        return True

    @commands.Cog.listener('on_user_update')
    async def change_to_kal_avatar(self, _: discord.User, user: discord.User):
        """Switches to kal's avatar any time they change it."""
        if user.id != 671777334906454026:
            return

        await self.bot.user.edit(avatar=await user.avatar.read())

    @commands.command()
    async def pyright(self, ctx: Context[Bot], *, code: CodeblockConverter):
        """Uses Pyright to do typechecking."""
        await ctx.trigger_typing()
        block = cast(Codeblock, code)

        with open('to_typecheck.py', 'w') as fh:
            fh.write(block.content)

        # As far as I know there's no facing API for this, so here we go.
        result = await run_shell('pyright --outputjson to_typecheck.py')

        # This is blocking, but since I don't realistically believe
        # I'll ever surpass a big enough file size (Especially with discord limits)
        # I don't really have to worry about it so much.
        os.remove('./to_typecheck.py')

        data = json.loads(result)
        diagnostics = data['generalDiagnostics']
        ret = []
        for element in diagnostics:
            sev: str = element['severity']
            message: str = element['message']
            ret.append(f'`{sev.capitalize()}` - {message}')

        ret.append(f'\nError Count: {data["summary"]["errorCount"]}')

        await ctx.send('\n'.join(ret))
