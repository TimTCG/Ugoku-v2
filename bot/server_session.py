import asyncio
import logging
import random
from datetime import datetime, timedelta
from typing import Optional, Callable

import discord
from librespot.audio import AbsChunkedInputStream

from bot.utils import update_active_servers
from bot.queue_view import QueueView
from config import AUTO_LEAVE_DURATION

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.session_manager import SessionManager


class ServerSession:
    def __init__(
        self,
        guild_id: int,
        voice_client: discord.VoiceClient,
        bot: discord.Bot,
        channel_id: int,
        session_manager: 'SessionManager'
    ):
        self.bot = bot
        self.guild_id = guild_id
        self.voice_client = voice_client
        self.queue = []
        self.to_loop = []
        self.last_played_time = datetime.now()
        self.loop_current = False
        self.loop_queue = False
        self.skipped = False
        self.shuffle = False
        self.original_queue = []
        self.shuffled_queue = []
        self.previous = False
        self.stack_previous = []
        self.is_seeking = False
        self.channel_id = channel_id
        self.session_manager = session_manager
        self.auto_leave_task = asyncio.create_task(
            self.check_auto_leave()
        )
        self.playback_start_time = None
        self.last_context = None
        self.volume = 100

    async def display_queue(
        self,
        ctx: discord.ApplicationContext
    ) -> None:
        view = QueueView(self.queue, self.to_loop, self.bot)
        await view.display(ctx)

    async def send_now_playing(
        self,
        ctx: discord.ApplicationContext
    ) -> None:
        # Retrieve the current track_info from the queue
        track_info: dict = self.queue[0]['track_info']
        embed: Optional[discord.Embed] = track_info['embed']
        title: str = track_info['display_name']
        url: str = track_info['url']
        title_markdown = f'[{title}](<{url}>)'

        if embed:
            # In case it requires additional api calls,
            # The embed is generated when needed only.
            embed = await embed()
            if len(self.queue) > 1:
                next_track_info = self.queue[1]['track_info']
                next_track = (
                    f'[{next_track_info["display_name"]}](<{next_track_info["url"]}>)')
            else:
                next_track = 'End of queue!'

            # Update the embed with remaining tracks
            embed.add_field(
                name="Remaining Tracks",
                value=str(len(self.queue) - 1),
                inline=True
            )
            embed.add_field(
                name="Next",
                value=next_track, inline=True
            )

            message = ''  # No need for a text message if embed
        else:
            message = f'Now playing: {title_markdown}'

        # Send the message or edit the previous message based on the context
        await ctx.send(content=message, embed=embed)

    async def seek(self, position: int):
        if not self.voice_client or not self.voice_client.is_playing():
            return False

        # Flag to indicate that the player is seeking
        self.is_seeking = True
        # Stop the current playback
        self.voice_client.stop()

        # Wait a short time to ensure the stop has been processed
        await asyncio.sleep(0.1)

        # Send "Seeking" message
        if self.last_context:
            await self.last_context.send(f"Seeking to {position} seconds")

        # Use start_playing with the new position
        await self.start_playing(self.last_context, start_position=position)

        return True

    async def start_playing(self, ctx: discord.ApplicationContext, start_position: int = 0) -> None:
        """Handles the playback of the next track in the queue."""
        self.last_context = ctx
        if not self.queue:
            logging.info(f'Playback stopped in {self.guild_id}')
            await update_active_servers(self.bot, self.session_manager.server_sessions)
            return  # No songs to play

        source = self.queue[0]['track_info']['source']
        # If source is a stream generator
        if isinstance(source, Callable):
            source = await source()  # Generate a fresh stream
            source.seek(167)  # Skip the non-audio content

        # Set up FFmpeg options for seeking
        # ffmpeg_options = {
        #     'options': f'-vn -ss {start_position} -af aresample=async=1 -ar 44100 -acodec pcm_s16le -ac 2'
        # }

        # ffmpeg_source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
        #     source,
        #     pipe=isinstance(source, AbsChunkedInputStream),
        #     **ffmpeg_options
        # ))

        # # Set the volume
        # ffmpeg_source.volume = self.volume / 100
        
        # That would be cool if we could have 2 modes, like one with volume controls,
        # the other with a better audio quality :11:
        
        ffmpeg_source = discord.FFmpegOpusAudio(
            source,
            pipe=isinstance(source, AbsChunkedInputStream),
            bitrate=510
        )

        self.voice_client.play(
            ffmpeg_source,
            after=lambda e=None: self.after_playing(ctx, e)
        )

        self.playback_start_time = datetime.now().isoformat()
        await update_active_servers(self.bot, self.session_manager.server_sessions)

        # Send "Now playing" at the end to slightly reduce audio latency
        if not self.is_seeking and (self.skipped or not self.loop_current):
            await self.send_now_playing(ctx)
            # Reset the skip flag
            self.skipped = False

        # Reset flags
        self.is_seeking = False
        self.previous = False
        

    async def add_to_queue(
        self,
        ctx: discord.ApplicationContext,
        tracks_info: list,
        source: str
    ) -> None:
        for track_info in tracks_info:
            queue_item = {'track_info': track_info, 'source': source}
            self.queue.append(queue_item)
            # Add to original queue for shuffle
            self.original_queue.append(queue_item)

        if self.shuffle:
            current_song = self.queue[0] if self.queue else None
            remaining_songs = self.queue[1:] if current_song else self.queue
            random.shuffle(remaining_songs)
            self.queue = [current_song] + \
                remaining_songs if current_song else remaining_songs

        # If only one song is added
        if len(tracks_info) == 1:
            title = tracks_info[0]['display_name']
            url = tracks_info[0]['url']
            await ctx.edit(content=f'Added to queue: [{title}](<{url}>) !')

        # If 2 or 3 songs are added
        elif len(tracks_info) in [2, 3]:
            titles_urls = ', '.join(
                f'[{track_info["display_name"]}](<{track_info["url"]}>)'
                for track_info in tracks_info
            )
            await ctx.edit(content=f'Added to queue: {titles_urls} !')

        # If more than 3 songs are added
        elif len(tracks_info) > 3:
            titles_urls = ', '.join(
                f'[{track_info["display_name"]}](<{track_info["url"]}>)'
                for track_info in tracks_info[:3]
            )
            additional_songs = len(tracks_info) - 3
            await ctx.edit(
                content=(
                    f'Added to queue: {titles_urls}, and '
                    f'{additional_songs} more song(s) !')
            )

        if not self.voice_client.is_playing() and len(self.queue) >= 1:
            await self.start_playing(ctx)

    async def play_previous(self, ctx: discord.ApplicationContext) -> None:
        self.previous = True
        self.queue.insert(0, self.stack_previous.pop())
        if self.voice_client.is_playing():
            self.voice_client.pause()
        await self.start_playing(ctx)

    async def skip_track(self, ctx: discord.ApplicationContext) -> bool:
        if not self.voice_client or not self.voice_client.is_playing():
            return False

        self.voice_client.pause()
        await self.play_next(ctx)
        return True

    def get_queue(self):
        return [
            {
                "title": track['track_info']['title'],
                "artist": track['track_info'].get('artist'),
                "album": track['track_info'].get('album'),
                "cover": track['track_info'].get('cover'),
                "duration": track['track_info'].get('duration'),
                "url": track['track_info']['url']
            }
            for track in self.queue
        ]

    async def shuffle_queue(self, is_active: bool) -> bool:
        if len(self.queue) <= 1:
            return  True # No need to shuffle if queue has 0 or 1 song

        current_song = self.queue[0]

        if is_active and not self.shuffle:
            self.shuffled_queue = self.queue[1:]
            random.shuffle(self.shuffled_queue)
            self.queue = [current_song] + self.shuffled_queue
            self.shuffle = True

        elif not is_active and self.shuffle:
            # Restore the original order
            current_index = self.original_queue.index(current_song)
            self.queue = [current_song] + \
                self.original_queue[current_index + 1:]
            self.shuffle = False
            
        return True

    def after_playing(
        self,
        ctx: discord.ApplicationContext,
        error: Exception
    ) -> None:
        self.last_played_time = datetime.now()
        if error:
            raise error

        if self.is_seeking:
            # If we're seeking, don't do anything
            return

        if self.queue and self.voice_client.is_connected():
            asyncio.run_coroutine_threadsafe(
                self.play_next(ctx), self.bot.loop
            )

    async def play_next(
        self,
        ctx: discord.ApplicationContext
    ) -> None:
        # Playing previous track ? :kanna_sus:
        if self.queue and not self.loop_current and not self.previous:
            self.stack_previous.append(self.queue[0])

        if self.loop_queue and not self.loop_current:
            self.to_loop.append(self.queue[0])

        if not self.loop_current:
            self.queue.pop(0)
        if not self.queue and self.loop_queue:
            self.queue, self.to_loop = self.to_loop, []

        await self.start_playing(ctx)

    def get_history(self):
        return [
            {
                "title": track['track_info']['title'],
                "artist": track['track_info'].get('artist'),
                "album": track['track_info'].get('album'),
                "cover": track['track_info'].get('cover'),
                "duration": track['track_info'].get('duration'),
                "url": track['track_info']['url']
            }
            for track in self.stack_previous
        ]

    async def toggle_loop(self, mode):
        if mode == 'noLoop':
            self.loop_current = False
            self.loop_queue = False
            response = 'You are not looping anymore.'
        elif mode == 'loopAll':
            self.loop_current = False
            self.loop_queue = True
            response = 'You are now looping the queue!'
        elif mode == 'loopOne':
            self.loop_current = True
            self.loop_queue = False
            response = 'You are now looping the current song!'
        else:
            return False

        # Send message to the server
        channel = self.bot.get_channel(self.channel_id)
        if channel and isinstance(channel, discord.TextChannel):
            await channel.send(response)
        return True

    async def check_auto_leave(self) -> None:
        while self.voice_client.is_connected():
            if not self.voice_client.is_playing():
                await asyncio.sleep(1)
                time_since_last_played = datetime.now() - self.last_played_time
                time_until_disconnect = timedelta(
                    seconds=AUTO_LEAVE_DURATION) - time_since_last_played

                logging.info(
                    'Time until disconnect due to '
                    f'inactivity in {self.guild_id}: '
                    f'{time_until_disconnect}'
                )

                if time_until_disconnect <= timedelta(seconds=0):
                    await self.voice_client.disconnect()
                    del self.session_manager.server_sessions[self.guild_id]
                    channel = self.bot.get_channel(self.channel_id)
                    if channel:
                        await channel.send('Baibai~')
                    logging.info(
                        f'Deleted audio session in {self.guild_id} '
                        'due to inactivity.'
                    )
                    break

            await asyncio.sleep(17)
