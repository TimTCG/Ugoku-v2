import discord
from discord.ext import commands

import os

from bot.line import get_stickerpack
from bot.exceptions import IncorrectURL


class Stickers(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.slash_command(
        name='get-stickers',
        description='Tải bộ sticker từ Line từ URL.'
    )
    async def stickers(
        self,
        ctx: discord.ApplicationContext,
        url: str
    ) -> None:
        if not url:
            await ctx.respond(
                'Hãy nhập URL của một bộ sticker nhaa. '
                'Vd: https://store.line.me/stickershop/product/1472670/'
            )
            return

        await ctx.respond('Chờ mình một lát nhaa~')

        try:
            zip_file = await get_stickerpack(url, ctx=ctx)
        except IncorrectURL:
            await ctx.edit(content='URL không hợp lệ. Hãy kiểm tra và thử lại nhé.')
            return

        await ctx.send(
            file=discord.File(zip_file),
            content=f'<@{ctx.author.id} ơi, xin lỗi vì để bạn chờ>, '
            "bộ sticker mà bạn yêu cầu ờ đây nhaa~"
        )

        # Clean up the file after sending
        os.remove(zip_file)

        await ctx.edit(content='Done!')


def setup(bot):
    bot.add_cog(Stickers(bot))
