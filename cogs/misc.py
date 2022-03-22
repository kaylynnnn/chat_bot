from deps import Bot, Context
from discord.ext import commands


async def setup(bot: Bot):
    await bot.add_cog(Misc(bot))


class Misc(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.command(aliases=['src'])
    async def source(self, ctx: Context):
        """Provides a link with the source code of the bot."""
        url = 'https://github.com/okaykallum/chat_bot'
        await ctx.send(f'Here\'s a link with the source of the bot:\n<{url}>')
