import discord
from deps import Bot, Context
from discord.ext import commands


async def setup(bot: Bot):
    await bot.add_cog(ErrorHandler(bot))


class ErrorHandler(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: Context[Bot], error: Exception | commands.CommandError):
        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.NotOwner):
            await ctx.send('\N{CROSS MARK}')
            return

        if isinstance(error, commands.BadColourArgument):
            await ctx.send(f'`{error.argument}` is an invalid colour.')
            return

        raise error