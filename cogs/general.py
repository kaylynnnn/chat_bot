from io import BytesIO

import discord
from deps import Bot, Context
from discord.ext import commands
from PIL import Image
from utils import to_thread


async def setup(bot: Bot):
    await bot.add_cog(General(bot))


class General(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @to_thread
    def generate_colour(self, colour: discord.Colour) -> BytesIO:
        """Uses PIL to generate a 128x128 image of a given colour."""
        buffer = BytesIO()
        with Image.new('RGB', (128, 128), colour.to_rgb()) as img:
            img.save(buffer, 'png')
        buffer.seek(0)
        return buffer

    @commands.command()
    async def ping(self, ctx: Context[Bot]):
        """Gets the bot's latency."""

    @commands.command(aliases=['color'])
    async def colour(self, ctx: Context[Bot], *, colour: discord.Colour):
        """Shows a representation of a given colour.
        Format could be the following:
        Name: `Red`
        Hex: `#ff0000`
        RGB: `rgb(255, 0, 0)`
        Note: Name vs RGB or Hex may produce different results."""
        image = await self.generate_colour(colour)
        file = discord.File(image, 'colour.png')

        embed = discord.Embed(colour=colour)
        embed.set_thumbnail(url='attachment://colour.png')
        embed.add_field(name='Hex', value=f'{colour}', inline=False)
        embed.add_field(name='RGB', value=f'rgb{colour.to_rgb()}', inline=False)

        await ctx.send(file=file, embed=embed)
