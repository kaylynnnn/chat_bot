import asyncio
import json
import os
import platform
from typing import NamedTuple

import discord
from deps import Bot, Context
from discord.ext import commands
from jishaku.codeblocks import codeblock_converter


async def run_shell(cmd: str) -> tuple[str, str]:
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await proc.communicate()

    return stdout.decode(), stderr.decode()


class Codeblock(NamedTuple):
    language: str
    content: str

    @classmethod
    async def convert(cls, _: Context, arg: str):
        result = codeblock_converter(arg)
        return Codeblock(result.language, result.content)


async def setup(bot: Bot):
    await bot.add_cog(Admin(bot))


class Admin(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def cog_check(self, ctx: Context) -> bool:
        check = await self.bot.is_owner(ctx.author)
        if not check:
            raise commands.NotOwner
        return True

    @commands.Cog.listener('on_user_update')
    async def change_to_kal_avatar(self, _: discord.User, user: discord.User):
        """Switches to kal's avatar any time they change it."""
        if user.id != 671777334906454026 or hash(user.avatar) == self.bot._kal_av_ash:
            return

        await self.bot.user.edit(avatar=await user.avatar.read())

    @commands.command()
    async def pyright(self, ctx: Context, *, code: Codeblock):
        """Uses Pyright to do typechecking."""
        await ctx.trigger_typing()

        with open('./to_typecheck.py', 'w') as fh:
            fh.write(code.content)

        # As far as I know there's no facing API for this, so here we go.
        # Also a hardcoded value here, but oh well.
        pyright_cmd = (
            '/home/kal/.local/bin/pyright'
            if platform.system() == 'Linux'
            else 'pyright'
        )
        result, err = await run_shell(f'{pyright_cmd} --outputjson ./to_typecheck.py')

        # This is blocking, but since I don't realistically believe
        # I'll ever surpass a big enough file size (Especially with discord limits)
        # I don't really have to worry about it so much.
        os.remove('./to_typecheck.py')

        try:
            data = json.loads(result)
        except json.JSONDecodeError:
            await ctx.send('Something went wrong hehe')
            return

        diagnostics = data['generalDiagnostics']
        ret = []
        for element in diagnostics:
            sev: str = element['severity']
            message: str = element['message']
            ret.append(f'`{sev.capitalize()}` - {message}')

        ret.append(f'\nError Count: {data["summary"]["errorCount"]}')

        await ctx.send('\n'.join(ret))
