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

        self.message: discord.Message | None = None

        self.last_time = None
        self.check_services.start()

    async def check_service(self, service: Service) -> None:
        try:
            async with self.bot.session.get(service.url):
                is_active = True
        except asyncio.TimeoutError:
            is_active = False

        service.last_result = is_active
        service.last_time = discord.utils.utcnow()

    async def update_status_message(self) -> None:
        embed = discord.Embed(title="Estado de serviços",
                              colour=0x00b0f4,
                              timestamp=self.last_time)

        for service in self.services:
            embed.add_field(name=f"Estado - {service.nome}",
                            value=f"{'Ativo  🟢' if service.last_result else 'Inativo 🔴'}",
                            inline=False)

        embed.set_image(url="https://cubedhuang.com/images/alex-knight-unsplash.webp")

        embed.set_thumbnail(url=self.bot.user.avatar.url)

        embed.set_footer(text="Last update",
                         icon_url="https://slate.dan.onl/slate.png")

        if self.message:
            await self.message.edit(content='', embed=embed)
        else:
            self.message = await self.channel.send(content='', embed=embed)
            with open('config.yaml', 'w') as f:
                config['bot']['message_id'] = self.message.id
                yaml.dump(config, f)

    @discord.utils.cached_property
    def channel(self) -> discord.TextChannel:
        channel = self.bot.guild.get_channel(config['bot']['channel_id'])

        if not channel:
            raise Exception('Invalid service channel ID provided')

        assert isinstance(channel, discord.TextChannel)
        return channel

    @tasks.loop(minutes=5)
    async def check_services(self) -> None:
        # TODO : add logs
        for service in self.services:
            await self.check_service(service)
        self.last_time = discord.utils.utcnow()
        await self.update_status_message()

    @check_services.before_loop
    async def before_check_services(self) -> None:
        await self.bot.wait_until_ready()
        # imporoviso para só pegar mensagem quando o bot estiver ativo
        if config['bot']['message_id'] is not None:
            self.message = await self.channel.fetch_message(config['bot']['message_id'])


async def setup(bot: CebraspeBot):
    await bot.add_cog(Services(bot))
