import discord
import logging
from discord.ext import commands
from config import (
    LANGUAGES,
    CHATBOT_WHITELIST,
    CHATBOT_ENABLED
)
from google.generativeai.types.generation_types import BlockedPromptException

if CHATBOT_ENABLED:
    from bot.chatbot.gemini import Gembot, active_chats


class Test(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.slash_command(
        name='translate',
        description='Dịch một câu sang bất kỳ ngôn ngữ nào.',
        integration_types={
            discord.IntegrationType.user_install
        }
    )
    async def translate(
        self,
        ctx: discord.ApplicationContext,
        query: str,
        language: discord.Option(
            str,
            choices=LANGUAGES,
            required=True,
            default='English'

        ),  # type: ignore
        nuance: discord.Option(
            str,
            choices=['Neutral', 'Casual', 'Formal'],
            required=True,
            default='Neutral'

        ),  # type: ignore
        ephemeral: bool = True
    ) -> None:
        await ctx.defer()
        await ctx.respond(
            content=Gembot.translate(
                query,
                language=language,
                nuance=nuance
            ),
            ephemeral=ephemeral
        )

    @commands.slash_command(
        name='ask',
        description='Hỏi Ugoku mọi thứ !',
        integration_types={
            discord.IntegrationType.user_install,
            discord.IntegrationType.guild_install
        }
    )
    async def ask(
        self,
        ctx: discord.ApplicationContext,
        query: str,
        ephemeral: bool = True
    ) -> None:
        guild_id = ctx.guild.id
        author_name = ctx.author.global_name

        if not CHATBOT_ENABLED:
            await ctx.respond("Tính năng chatbot chưa được bật")
            return
        if ctx.guild.id not in CHATBOT_WHITELIST:
            await ctx.respond("Máy chủ này không được phép sử dụng lệnh.")
            return

        await ctx.defer()

        # Create/Use a chat
        if guild_id not in active_chats:
            chat = Gembot(guild_id)
        chat = active_chats.get(guild_id)

        # Remove continuous chat notice (if enabled the msg before)
        if chat.status == 1:
            chat.status = 2

        # Create response
        try:
            reply = await chat.send_message(
                user_query=query,
                author=author_name
            )

        except BlockedPromptException:
            await ctx.respond(
                "*filtered*",
                ephemeral=ephemeral
            )
            logging.error(f"Response blocked by Gemini in {chat.id_}")
            return

        except BlockedPromptException:
            logging.error(
                "Prompt against Gemini's policies! "
                "Please change it and try again."
            )
            return

        # Response
        formatted_reply = (
            f"-# {author_name}: {query}\n{chat.format_reply(reply)}")
        await ctx.respond(formatted_reply, ephemeral=ephemeral)

        # Memory
        await chat.memory.store(
            query,
            author=author_name,
            id=guild_id
        )


def setup(bot):
    bot.add_cog(Test(bot))
