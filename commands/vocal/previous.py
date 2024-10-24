import discord
from discord.ext import commands
from bot.vocal.session_manager import session_manager as sm

from bot.vocal.server_session import *


class Previous(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    async def execute_previous(
        self,
        ctx: discord.ApplicationContext
    ) -> None:
        guild_id = ctx.guild.id
        session = sm.server_sessions.get(guild_id)

        if session is None:
            await ctx.respond('Không có phiên hoạt động')
            return

        if not session.stack_previous:
            await ctx.respond("Không có bài hát nào phát trước đó!")
            return

        await ctx.respond('Đang phát bài hát trước đó!')
        await session.play_previous(ctx)

    @commands.slash_command(
        name='previous',
        description='Phát bài hát trước đó.'
    )
    async def previous(self, ctx: discord.ApplicationContext) -> None:
        await self.execute_previous(ctx)

def setup(bot):
    bot.add_cog(Previous(bot))
