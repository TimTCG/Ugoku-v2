import logging
from bot.utils import send_response
from typing import Optional

import discord
from discord.ext import commands
from bot.vocal.session_manager import session_manager as sm


class Loop(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    async def execute_loop(
        self,
        ctx: discord.ApplicationContext,
        mode: str,
        send: bool = False
    ) -> None:
        guild_id: int = ctx.guild.id
        session = sm.server_sessions.get(guild_id)
        respond = (ctx.send if send else ctx.respond)

        if not session:
            await send_response(
                respond,
                "Kohane chưa được kết nối vào kênh thoại!",
                guild_id
            )
            return

        mode = mode.lower()

        if mode == 'song':
            session.loop_current = not session.loop_current
            response = (
                "Bạn đang lặp lại bài hát hiện tại!"
                if session.loop_current
                else "Bạn đang không lặp lại bài hát hiện tại."
            )

        elif mode == 'queue':
            session.loop_queue = not session.loop_queue

            if session.loop_queue:
                session.loop_current = False
                response = "Bạn đang lặp lại hàng chờ hiện tại!"
            else:
                session.to_loop.clear()
                response = "Bạn đang không lặp lại hàng chờ hiện tại."

        else:
            response = "oi"

        await send_response(respond, response, guild_id)

    @commands.slash_command(
        name='loop',
        description='Lặp lại/Không lặp lại những gì bạn đang nghe trong kênh thoại.'
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
