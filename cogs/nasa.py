import os
import aiohttp
import discord
from discord.ext import commands

NASA_API_KEY = os.getenv("NASA_API_KEY")


class NASA(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def apod(self, ctx):

        url = "https://api.nasa.gov/planetary/apod"

        params = {
            "api_key": NASA_API_KEY
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:

                if response.status != 200:
                    await ctx.send("❌ Errore nel contattare la NASA API.")
                    return

                data = await response.json()

        title = data.get("title", "NASA APOD")
        explanation = data.get("explanation", "Nessuna descrizione.")
        image_url = data.get("url")
        date = data.get("date")

        embed = discord.Embed(
            title=title,
            description=explanation,
            color=discord.Color.blue()
        )

        embed.set_image(url=image_url)
        embed.set_footer(text=f"NASA APOD • {date}")

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(NASA(bot))