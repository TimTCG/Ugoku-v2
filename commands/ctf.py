import discord
import logging
import requests
import os
import mysql.connector
import datetime

from dotenv import load_dotenv
from discord.ext import commands
from dateutil.relativedelta import relativedelta

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

load_dotenv(".env", override=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0"
}

class CTFTimes(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    async def ctf_information(self, ctx: discord.ApplicationContext, guild: discord.Guild, event_id: str):
        """
        Fetch and display CTF information.
        """
        try:
            response = requests.get(
                f"https://ctftime.org/api/v1/events/{event_id}/", headers=HEADERS
            )
            response.raise_for_status()
            info = response.json()

            title = info["title"]
            url = info["url"]
            start = info["start"]
            end = info["finish"]
            description = info["description"]
            weight = info["weight"]
            onsite = info["onsite"]
            format_type = f"{'Online' if not onsite else 'Offline'} {info['format']}"

            image = info["logo"] if info["logo"] else "https://play-lh.googleusercontent.com/uiZnC5tIBpejW942OXct4smbaHmSowdT5tLSi28Oeb2_pMLPCL-VJqdGIH6ZO3A951M=w480-h960"

            start_ts = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S%z").timestamp()
            end_ts = datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M:%S%z").timestamp()

            embed = discord.Embed(
                title=title,
                description=description,
                color=discord.Color.blue(),
                url=url,
            )
            embed.set_thumbnail(url=image)
            embed.add_field(name="URL", value=url, inline=False)
            embed.add_field(name="Start", value=f"<t:{int(start_ts)}:f>", inline=False)
            embed.add_field(name="End", value=f"<t:{int(end_ts)}:f>", inline=False)
            embed.add_field(name="CTF Weight", value=weight, inline=False)
            embed.add_field(name="Format", value=format_type, inline=False)
            
            await ctx.respond(embed=embed)
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching CTF information: {e}")
            await ctx.respond("Có lỗi khi lấy thông tin các giải CTF", ephemeral=True)
        except ValueError as e:
            logging.error(f"Error decoding JSON response: {e}")
            await ctx.respond("Có lỗi khi giải mã phản hồi JSON.", ephemeral=True)


    async def upcoming_ctf(self, ctx: discord.ApplicationContext, guild: discord.Guild):
        now = datetime.datetime.utcnow().timestamp()
        next_week = datetime.datetime.utcnow() + relativedelta(days=+7)
        future = next_week.timestamp()
        try:
            response = requests.get(
                f"https://ctftime.org/api/v1/events/?limit=5&start={int(now)}&finish={int(future)}",
                headers=HEADERS
            )
            response.raise_for_status()
            info = response.json()

            embed = discord.Embed(
                title="Các giải CTF sắp tới",
                description="Đây là các giải CTF trong vòng 7 ngày sắp tới.",
                color=discord.Color.blue()
            )

            for event in info:
                name = event["title"]
                url = event["url"]
                start = event["start"]
                event_id = event["id"]

                # Parse the start date
                start_dt = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S%z")
                start_ts = int(start_dt.timestamp())

                embed.add_field(name=name, value=f"[Link]({url})", inline=True)
                embed.add_field(name="Event ID", value=event_id, inline=True)
                embed.add_field(name="Start Date", value=f"<t:{start_ts}:f>", inline=True)

            await ctx.respond(embed=embed)
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching upcoming CTF events: {e}")
            await ctx.respond("Có lỗi khi lấy thông tin các giải CTF", ephemeral=True)
        except ValueError as e:
            logging.error(f"Error decoding JSON response: {e}")
            await ctx.respond("Có lỗi khi giải mã phản hồi JSON.", ephemeral=True)
            
        
    @commands.slash_command(
        name="ctf-upcoming",
        description="Lấy thông tin các giải CTF sắp tới",
    )
    async def ctfupcoming(self, ctx: discord.ApplicationContext):
        """
        Command to fetch upcoming CTF events.
        """
        guild = ctx.guild
        await self.upcoming_ctf(ctx, guild)
        

    @commands.slash_command(
        name='ctf-info',
        description='Tìm hiểu thêm thông tin về một giải CTF',
    )
    async def ctfinfo(self, ctx: discord.ApplicationContext, event_id: str):
        """
        Command to fetch CTF information.
        """
        guild = ctx.guild
        await self.ctf_information(ctx, guild, event_id)
        


def setup(bot):
    bot.add_cog(CTFTimes(bot))
    
