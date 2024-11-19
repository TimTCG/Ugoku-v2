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
        description='Tải một bộ nhãn dán từ Line.',
        integration_types={
            discord.IntegrationType.guild_install,
            discord.IntegrationType.user_install
        }
    )
    async def stickers(
        self,
        ctx: discord.ApplicationContext,
        url: discord.Option(
            str,
            required=True
        )  # type: ignore
    ) -> None:
        await ctx.respond('Chờ mình một lát nha~')

        try:
            zip_file = await get_stickerpack(url, ctx=ctx)
        except IncorrectURL:
            await ctx.edit(
                content="URL không hợp lệ. Hãy kiểm tra và thử lại nhé."
                "\nVí dụ: "
                "https://store.line.me/stickershop/product/20347097/en"
                )
            return

        await ctx.edit(
            file=discord.File(zip_file),
            content="Bộ nhãn dán mà bạn yêu cầu đây nha~"
        )
        # Clean up the file after sending
        os.remove(zip_file)


def setup(bot):
    bot.add_cog(Stickers(bot))
