from bot.vocal.youtube import Youtube
import api.api as api
from config import COMMANDS_FOLDER, SPOTIFY_ENABLED, CHATBOT_ENABLED
import discord
import os
import logging
import asyncio
from dotenv import load_dotenv

load_dotenv()


if SPOTIFY_ENABLED:
    from bot.vocal.spotify import SpotifySessions, Spotify

if CHATBOT_ENABLED:
    from bot.chatbot.vector_recall import Memory


load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
DEV_TOKEN = os.getenv('DEV_TOKEN')


# Init bot
intents = discord.Intents.default()
intents.message_content = True
loop = asyncio.get_event_loop()
bot = discord.Bot(intents=intents, loop=loop)
server = api.server
api.bot = bot


@bot.event
async def on_ready() -> None:
    logging.info(f"{bot.user} đang chạy !")
    if SPOTIFY_ENABLED:
        spotify_sessions = SpotifySessions()
        await spotify_sessions.init_spotify()
        spotify = Spotify(spotify_sessions)
        bot.spotify = spotify
        bot.downloading = False
    bot.youtube = Youtube()


for filepath in COMMANDS_FOLDER.rglob('*.py'):
    relative_path = filepath.relative_to(COMMANDS_FOLDER).with_suffix('')
    module_name = f"commands.{relative_path.as_posix().replace('/', '.')}"

    logging.info(f'Loading {module_name}')
    bot.load_extension(module_name)


async def start() -> None:
    await asyncio.gather(bot.start(DEV_TOKEN), server.serve())

try:
    loop.run_until_complete(start())
finally:
    if not bot.is_closed():
        loop.run_until_complete(bot.close())
    if server.started:
        loop.run_until_complete(server.shutdown())
