import discord
from discord.ext import commands
import requests

class IPLookup(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ip(self, ctx, address: str):
        url = f"http://ip-api.com/json/{address}"

        response = requests.get(url)
        data = response.json()

        if data["status"] != "success":
            await ctx.reply("❌ Invalid IP")
            return

        embed = discord.Embed(
            title=f"🌐 Information about IP: {address}",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="🌍 Country",
            value=data.get("country", "N/A")
        )
        embed.add_field(
            name="🏙️ City",
            value=data.get("city", "N/A")
        )
        embed.add_field(
            name="📡 ISP",
            value=data.get("isp", "N/A"),
            inline=False
        )
        embed.add_field(
            name="🏢 Organization",
            value=data.get("org", "N/A"),
            inline=False
        )
        embed.add_field(
            name="🕒 Timezone",
            value=data.get("timezone", "N/A")
        )
        embed.add_field(
            name="📍 Coordinates",
            value=f"{data.get('lat')}, {data.get('lon')}"
        )
        await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(IPLookup(bot))