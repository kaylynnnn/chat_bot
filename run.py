import asyncio
from deps import Bot
import toml


async def main():
    with open('config.toml') as fh:
        config = toml.load(fh)

    bot = Bot(config=config)
    async with bot:
        await bot.start()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
