import os
from typing import Sequence

import aiohttp
import discord
import yaml
from discord import Guild
from discord.ext import commands

with open('config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)


class CebraspeBot(commands.Bot):
    def __init__(self):
        self.session = None
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='?', intents=intents)

    @discord.utils.cached_property
    def guilds(self) -> discord.Guild:
        guild = self.get_guild(config['bot']['guild_id'])

        if not guild:
            raise Exception('Invalid guild Id provided')

        return guild

    async def on_ready(self):
        print(f'Online with {len(self.users)} users')

    async def setup_hook(self) -> None:
        timeout = aiohttp.ClientTimeout(total=10)
        self.session = aiohttp.ClientSession(timeout=timeout)

        await self.load_extension('services')
        await self.load_extension('jishaku')

    async def close(self) -> None:
        await self.session.close()
        await super().close()
