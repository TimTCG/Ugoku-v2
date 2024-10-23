import discord
from discord.ext import commands
from bot.vocal.session_manager import session_manager


class Resume(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    async def execute_resume(self, ctx: discord.ApplicationContext) -> None:
        session = session_manager.server_sessions.get(ctx.guild.id)

        if not session:
            await ctx.respond('Không có gì để tiếp tục!')
            return

        voice_client = session.voice_client

        if voice_client.is_paused():
            voice_client.resume()
            await ctx.respond('Đã tiếp tục!')
        else:
            await ctx.respond('Âm thành chưa có dừng phát mà.')

    @commands.slash_command(
        name='resume',
        description='Tiếp tục bài hát hiện tại.'
    )
    async def resume(self, ctx: discord.ApplicationContext) -> None:
        await self.execute_resume(ctx)


def setup(bot):
    bot.add_cog(Resume(bot))
