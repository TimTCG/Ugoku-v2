import discord
from discord.ext import commands
import config

import logging


logger = logging.getLogger(__name__)


class Ping(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.slash_command(
        name="ping",
        description='Kiểm tra phản hổi của Ugoku !'
    )
    async def ping(self, ctx: discord.ApplicationContext) -> None:
        latency = round(self.bot.latency*1000, 2)
        await ctx.respond(f'あわあわあわわわ ! {latency}ms')
        logging.info(f'Độ trễ khi được nhắc đến: {latency}ms.')


def setup(bot):
    bot.add_cog(Ping(bot))
