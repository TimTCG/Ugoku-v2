import asyncio
import os
import logging
import urllib.parse

import discord
from discord.ext import commands
from deezer.errors import DataException
from google.cloud import storage
from datetime import timedelta

from config import DEEZER_ENABLED
from bot.utils import cleanup_cache, tag_flac_file, get_cache_path

class DeezerDownload(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.gcs_client = storage.Client()
        self.bucket_name = "ugoku"  # Ensure this is set in your environment
        self.custom_domain = os.getenv("CUSTOM_DOMAIN")  # Optional custom domain

    async def upload_to_gcs(self, file_path, display_name):
        bucket = self.gcs_client.bucket(self.bucket_name)
        blob = bucket.blob(f"tracks/{display_name}.flac")
        
        try:
            blob.upload_from_filename(file_path, content_type="audio/flac")
            signed_url = blob.generate_signed_url(
            expiration=timedelta(days=7),
            method="GET"
        )
            return signed_url
        except Exception as e:
            logging.error(f"GCS Upload failed: {e}")
            return None

    @commands.slash_command(
        name='dzdl',
        description='Tải nhạc chất lượng cao từ Deezer',
        integration_types={
            discord.IntegrationType.guild_install,
            discord.IntegrationType.user_install,
        }
    )
    async def dzdl(self, ctx: discord.ApplicationContext, query: str) -> None:
        if not DEEZER_ENABLED:
            await ctx.respond(content='Các tính năng Deezer chưa được bật')
            return

        await ctx.respond('Chờ mình một lát nha~')
        self.bot.downloading = True
        
        try:
            track = await self.bot.deezer.get_track_from_query(query)
            if not track:
                await ctx.edit(content="Không tìm thấy bài hát!")
                return
        except DataException:
            await ctx.edit(content="Không tìm thấy bài hát!")
            return

        await cleanup_cache()
        cache_id = f"deezer{track['id']}"
        file_path = get_cache_path(cache_id.encode('utf-8'))

        if not file_path.is_file():
            file_path = await self.bot.deezer.download(track)

        display_name = f"{track['artist']} - {track['title']}"
        await tag_flac_file(
            file_path,
            title=track['title'],
            date=track['date'],
            artist=track['artists'],
            album=track['album'],
            album_cover_url=track['cover']
        )

        size = os.path.getsize(file_path)
        size_limit = ctx.guild.filesize_limit if ctx.guild else 26214400

        if size < size_limit:
            try:
                await ctx.edit(
                    content="Here you go!",
                    file=discord.File(file_path, filename=f"{display_name}.flac")
                )
                return
            except discord.errors.HTTPException as e:
                if e.status == 413:
                    logging.error(f"File not uploaded: {cache_id} is too big: {size} bytes")

        await ctx.edit(content="Đang tải lên Cloud...")

        file_url = await self.upload_to_gcs(file_path, display_name)
        if file_url:
            await ctx.edit(content=f"Tệp quá lớn, hãy sử dụng link này nhé (Link chỉ có hạn trong 7 ngày): {file_url}")
        else:
            await ctx.edit(content="Không thể tải lên Cloud")


def setup(bot):
    bot.add_cog(DeezerDownload(bot))
