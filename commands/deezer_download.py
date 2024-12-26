import asyncio
import os
import logging

import discord
from discord.ext import commands
from deezer.errors import DataException
import boto3
from botocore.exceptions import BotoCoreError, ClientError

from config import DEEZER_ENABLED
from bot.utils import cleanup_cache, tag_flac_file, get_cache_path

end_url=os.getenv("ENDPOINT_URL")

# Initialize the R2 client
r2_client = boto3.client(
    's3',
    endpoint_url=end_url,
    aws_access_key_id=os.getenv("AWS_SECRET_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_KEY")
)

class DeezerDownload(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.slash_command(
        name='dzdl',
        description='Tải bài hát chất lượng cao từ Deezer.',
        integration_types={
            discord.IntegrationType.guild_install,
            discord.IntegrationType.user_install,
        }
    )
    async def dzdl(
        self,
        ctx: discord.ApplicationContext,
        query: str
    ) -> None:
        if not DEEZER_ENABLED:
            await ctx.respond(content='Tính năng Deezer chưa được bật.')
            return

        await ctx.respond('Chờ mình một lát nha~')

        try:
            track = await self.bot.deezer.get_stream_url_from_query(query)
            logging.info(f"Track data: {track}")
        except DataException:
            await ctx.edit(content="Không tìm thấy bài hát !")
            return
        if not track:
            await ctx.edit(content="Không tìm thấy bài hát !")
            return

        # Set the cache path
        cleanup_cache()
        file_path = get_cache_path(str(track['track_id']).encode('utf-8'))

        # Download
        if not file_path.is_file():
            file_path = await asyncio.to_thread(self.bot.deezer.download, track)

        # Tag the file
        display_name = f"{track['artist']} - {track['title']}"
        await tag_flac_file(
            file_path,
            title=track['title'],
            date=track['date'],
            artist=track['artists'],
            album=track['album'],
            album_cover_url=track['cover']
        )

        display_name_link = display_name.replace(' ','%20')

        size = os.path.getsize(file_path)
        if size < ctx.guild.filesize_limit:
            await ctx.edit(
                content="Của bạn đây !",
                file=discord.File(
                    file_path,
                    filename=f"{display_name}.flac"
                )
            )
        else:
            try:
                bucket_name = os.getenv("BUCKET_NAME")
                key = f"tracks/{display_name}.flac"
                key_link = f"{bucket_name}/tracks/{display_name_link}.flac"
                
                r2_client.upload_file(file_path, bucket_name, key)

                custom_domain= os.getenv("CUSTOM_DOMAIN")
                if custom_domain:
                    public_url = f"{custom_domain}/{key_link}"
                else:
                    public_url = f"{end_url}/{key_link}"

                await ctx.edit(content=f"Tệp quá lớn. Bạn có thể tải tại đây: {public_url}")
            except (BotoCoreError, ClientError) as e:
                logging.error(f"Error uploading to R2: {e}")
                await ctx.edit(content="Tải thất bại: Không thể tải lên R2.")
def setup(bot):
    bot.add_cog(DeezerDownload(bot))