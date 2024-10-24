from typing import Union, Optional

from discord.ext import commands
import discord

from bot.vocal.session_manager import session_manager
from bot.vocal.audio_source_handlers import play_spotify, play_custom, play_onsei
from bot.utils import is_onsei
from bot.search import is_url
from config import SPOTIFY_ENABLED


class Play(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    async def execute_play(
        self, 
        ctx: discord.ApplicationContext, 
        query: str,
        source: str,
        interaction: Optional[discord.Interaction] = None
    ) -> None:
        if interaction:
            respond = interaction.response.send_message
            edit = interaction.edit_original_response
        else:
            respond = ctx.respond
            edit = ctx.edit

        # Connect to the voice channel
        session = await session_manager.connect(ctx, self.bot)
        if not session:
            await respond('Bạn đang không ở trong kênh thoại!')
            return

        await respond('Chờ mình một lát nha~')
        
        source = source.lower()

        # Detect if the query refers to an Onsei
        if source == 'onsei' or is_onsei(query):
            await play_onsei(ctx, query, session)

        # If the query is custom or an URL not from Spotify
        elif (source == 'custom'
              or (is_url(query) and not is_url(query, from_=['open.spotify.com']))):
            await play_custom(ctx, query, session)

        # Else, search Spotify
        elif source == 'spotify':
            if not SPOTIFY_ENABLED:
                await edit(content='Các tính năng Spotify hiện chưa được bật.')
                return
            await play_spotify(ctx, query, session, interaction=interaction)

        else:
            await edit(content='ôi lmao')

    @commands.slash_command(
        name='play',
        description='Chọn một bài hát để phát.'
    )
    async def play(
        self,
        ctx: discord.ApplicationContext,
        query: str,
        source: discord.Option(
            str,
            choices=['Spotify', 'Custom', 'Onsei'],
            default='Spotify'
        )  # type: ignore
    ) -> None:
        await self.execute_play(ctx, query, source)


def setup(bot):
    bot.add_cog(Play(bot))
