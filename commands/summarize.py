import discord
from discord.ext import commands

from config import CHATBOT_ENABLED, CHATBOT_WHITELIST


if CHATBOT_ENABLED:
    from bot.summaries import Summaries

    class Summarize(commands.Cog):
        def __init__(self, bot) -> None:
            self.bot = bot

        @commands.slash_command(
            name='summarize',
            description='Tóm tắt một đoạn văn bản, một file âm thanh, hoặc một video YouTube.'
        )
        async def summarize(
            self,
            ctx: discord.ApplicationContext,
            query: str,
            type: discord.Option(
                str,
                choices=['Text', 'Youtube video']
            )  # type: ignore
        ) -> None:
            if not CHATBOT_ENABLED or not ctx.guild.id in CHATBOT_WHITELIST:
                await ctx.respond('Tóm tắt không khả dụng trong máy chủ của bạn~')
                return

            await ctx.respond('Chờ mình một lát nhé~')
            if type == 'Youtube video':
                query = await Summaries.get_youtube_transcript_text(url=query)

            # Prepare the summary
            text = await Summaries.summarize(query)
            if not text:
                await ctx.edit(
                    content='Có lỗi xảy ra thì tạo bản tóm tắt!')

            # Prepare the embed
            # ...
            await ctx.respond(text)
else:
    class Summarize(commands.Cog):
        def __init__(self, bot) -> None:
            self.bot = bot


def setup(bot):
    bot.add_cog(Summarize(bot))
