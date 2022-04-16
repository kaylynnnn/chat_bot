import traceback
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
            # So ideally these are sent to a channel rather than DMs
            # but since I have no plans of the bot growing I don't really care myself
            # may change in the future if the bot does grow but again, no plans for that.
            await ctx.send(
                'Oh, an error happend.\n'
                'I\'ll report this to my developer, thank you.'
            )
            primary_owner: int = self.bot.config['owner_ids'][0]  # type: ignore
            user = await self.bot.try_user(primary_owner)

            embed = discord.Embed(
                title='An error occurred!',
                description=(
                    f'Guild: {getattr(ctx.guild, "id", "DMs")}\n'
                    f'Channel: {getattr(ctx.channel, "id", "DMs")}\n'
                    f'Author: {ctx.author.id}'
                )
            )
            embed.add_field(
                name='Traceback',
                value=f'```py\n{traceback.format_tb(error.__traceback__)}```'
            )

            await user.send(embed=embed)
            raise error
