import os
import logging

import discord
from discord.ext import commands

from config import (
    CHATBOT_WHITELIST,
    CHATBOT_ENABLED,
    ALLOW_CHATBOT_IN_DMS
)
from google.generativeai.types.generation_types import (
    BlockedPromptException,
    StopCandidateException
)

if CHATBOT_ENABLED:
    from bot.chatbot.gemini import Gembot, active_chats

    class Chatbot(commands.Cog):
        def __init__(self, bot) -> None:
            self.bot = bot

        @commands.slash_command(
            name="reset_chatbot",
            description="Resets the chatbot."
        )
        async def reset_chatbot(self, ctx: discord.ApplicationContext) -> None:
            Gembot(ctx.guild_id)
            await ctx.respond("Done!")

        @commands.Cog.listener()
        async def on_message(self, message: discord.Message) -> None:
            # Ignore messages from the bot itself
            if message.author == self.bot.user:
                return

            # Handle record requests
            record_handled = await handle_record_request(self.bot, message)
            if record_handled:
                return

            # Chatbot interaction logic
            server_id = message.guild.id if message.guild else message.author.id  # Use author ID for DM interactions
            if server_id not in active_chats:
                active_chats[server_id] = Gembot(server_id)
            
            chat = active_chats[server_id]
            if await chat.is_interacting(message):
                async with message.channel.typing():
                    try:
                        params = await chat.get_params(message)
                        reply = await chat.send_message(*params)
                        formatted_reply = chat.format_reply(reply)
                        await message.channel.send(formatted_reply)

                        await chat.memory.store(
                            params[0],
                            author=message.author.name,
                            id=server_id,
                        )
                    except StopCandidateException:
                        await message.channel.send("*filtered*")
                    except BlockedPromptException:
                        logging.error("Blocked prompt!")

else:
    class Chatbot(commands.Cog):
        def __init__(self, bot) -> None:
            self.bot = bot

def setup(bot):
    bot.add_cog(Chatbot(bot))