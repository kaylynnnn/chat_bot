from io import BytesIO
import textwrap
import time

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
    async def ping(self, ctx: Context):
        """Gets the bot's latency."""
        async with self.bot.pool.acquire() as conn:
            db_start = time.perf_counter()
            await conn.execute('SELECT 1;')
            db_end = time.perf_counter()

        type_start = time.perf_counter()
        await ctx.trigger_typing()
        type_end = time.perf_counter()

        message = f'''DB Latency: {round((db_end - db_start) * 1000, 2)} ms
        Round Trip Latency: {round((type_end - type_start) * 1000, 2)} ms
        Heartbeat Latency: {round(self.bot.latency * 1000, 2)} ms
        '''

        embed = discord.Embed(description=textwrap.dedent(message))
        await ctx.send(embed=embed)

    @commands.command(aliases=['color'])
    async def colour(self, ctx: Context, *, colour: discord.Colour):
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
