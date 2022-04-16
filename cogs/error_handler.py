import discord
from deps import Bot, Context
from discord.ext import commands


async def setup(bot: Bot):
    await bot.add_cog(ErrorHandler(bot))


class ErrorHandler(commands.Cog):
    STD_ERRS = (
        commands.MissingRequiredArgument,
        commands.MissingPermissions,
        commands.BotMissingPermissions,
    )

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(
        self,
        ctx: Context,
        error: Exception | commands.CommandError | discord.errors.DiscordException,
    ):
        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.NotOwner):
            await ctx.send('\N{CROSS MARK}')
        elif isinstance(error, commands.BadColourArgument):
            await ctx.send(f'`{error.argument}` is an invalid colour.')
        elif isinstance(error, self.STD_ERRS):
            await ctx.send(str(error))
        else:
            raise error
