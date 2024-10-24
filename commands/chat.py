import discord
from discord.ext import commands
from bot.vocal.session_manager import session_manager as sm

from config import CHATBOT_WHITELIST, CHATBOT_ENABLED

if CHATBOT_ENABLED:
    from bot.chatbot import Chat, active_chats

    class Chatbot(commands.Cog):
        def __init__(self, bot) -> None:
            self.bot = bot

        @commands.Cog.listener()
        async def on_message(self, message: discord.Message):
            server_id = message.guild.id

            # Only allow whitelisted servers
            if not server_id in CHATBOT_WHITELIST:
                return

            # Ignore if the message is from Ugoku !
            if message.author == self.bot.user:
                return

            # Create/Use a chat
            if server_id not in active_chats:
                active_chats[server_id] = Chat(server_id)
            chat: Chat = active_chats[server_id]
            
            # Neko arius
            lowered_msg = message.content.lower()
            if any(lowered_msg.startswith(neko) for neko in ['-neko', '- neko']):
                await message.channel.send('Arius')
                return

            if await chat.is_interacting(message):
                async with message.channel.typing():
                    reply = await chat.generate_response(message)
                    # With chat status
                    formatted_reply = chat.format_reply(reply)
                await message.channel.send(formatted_reply)
                await chat.post_prompt()

# Changed to async setup function
async def setup(bot):
    if CHATBOT_ENABLED:
        await bot.add_cog(Chatbot(bot))