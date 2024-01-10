import asyncio
import datetime
from dataclasses import dataclass

import discord
import yaml
from discord.ext import commands, tasks

from bot import CebraspeBot

with open('config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

CHANNEL_ID = config['bot']['channel_id']


@dataclass
class Service:
    url: str
    nome: str
    last_result: bool | None
    last_time: datetime.datetime | None


class Services(commands.Cog):

    def __init__(self, bot: CebraspeBot):
        self.bot: CebraspeBot = bot

        self.services = []

        for service in config['services']:
            service_obj = Service(
                url=service['url'],
                nome=service['nome'],
                last_result=None,
                last_time=discord.utils.utcnow())
            self.services.append(service_obj)

        self.status_messages = {}
        self.check_services.start()

    async def check_service(self, service: Service) -> None:
        try:
            async with self.bot.session.get(service.url):
                is_active = True
        except asyncio.TimeoutError:
            is_active = False

        service.last_result = is_active
        service.last_time = discord.utils.utcnow()
        await self.update_status_message(service)

    async def update_status_message(self, service: Service) -> None:
        print('updating status message')
        content = (f'{service.nome} status: {'Active' if service.last_result else 'Inactive'}'
                   f' - Last checked on: {service.last_time.strftime('%c')}')
        if service.nome in self.status_messages:
            message_id = self.status_messages[service.nome]
            message = await self.channel.fetch_message(message_id)
            await message.edit(content=content)
        else:
            new_message = await self.channel.send(content)
            self.status_messages[service.nome] = new_message.id

    @discord.utils.cached_property
    def channel(self) -> discord.TextChannel:
        channel = self.bot.guild.get_channel(config['bot']['channel_id'])

        if not channel:
            raise Exception('Invalid service channel ID provided')

        assert isinstance(channel, discord.TextChannel)
        return channel

    @tasks.loop(seconds=12)
    async def check_services(self) -> None:
        # TODO : add logs
        print('checking services')
        for service in self.services:
            await self.check_service(service)

    @check_services.before_loop
    async def before_check_services(self) -> None:
        print('waiting for bot')
        await self.bot.wait_until_ready()


async def setup(bot: CebraspeBot):
    await bot.add_cog(Services(bot))
