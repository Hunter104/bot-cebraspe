import os

from bot import CebraspeBot


def main():
    bot = CebraspeBot()
    token = os.environ['TOKEN']
    bot.run(token)

if __name__ == '__main__':
    main()
