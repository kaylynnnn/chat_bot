from deps import Bot
import toml


def main():
    with open('config.toml') as fh:
        config = toml.load(fh)

    bot = Bot(config=config)
    bot.run()


if __name__ == '__main__':
    main()
