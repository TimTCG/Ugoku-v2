import discord
from discord.ext import commands
from bot.vocal.session_manager import session_manager as sm


class Loop(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    async def execute_loop(
        self,
        ctx: discord.ApplicationContext,
        mode: str
    ) -> None:
        session = sm.server_sessions.get(ctx.guild.id)

        if not session:
            await ctx.respond('Ugoku chưa được kết nối tới kênh thoại!')
            return

        mode = mode.lower()

        if mode == 'song':
            session.loop_current = not session.loop_current

            if session.loop_current:
                response = 'Bạn đang lặp lại bài hát hiện tại'
            else:
                response = 'Bạn đã dừng lặp lại bài hát hiện tại.'

        elif mode == 'queue':
            session.loop_queue = not session.loop_queue

            if session.loop_queue:
                response = 'Bạn đang lặp lại hàng chờ hiện tại!'
                # Disable song loop when looping the queue
                session.loop_current = False
            else:
                # Clear loop queue when stopping queue loop
                session.to_loop = []
                response = 'Bạn đã dừng lặp lại hàng chờ hiện tại.'

        else:
            response = 'oi'

        await ctx.respond(response)

    @commands.slash_command(
        name='loop',
        description='Lặp lại/Dừng lặp lại bài hát đang phát trong kênh thoại.'
    )
    async def loop(
        self,
        ctx: discord.ApplicationContext,
        mode: discord.Option(
            str,
            choices=['Song', 'Queue'],
            default='Queue'
        )  # type: ignore
    ) -> None:
        await self.execute_loop(ctx, mode)


def setup(bot):
    bot.add_cog(Loop(bot))
