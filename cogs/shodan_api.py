import discord
from discord.ext import commands
import shodan
import os
import asyncio

SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")

class ShodanCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        if not SHODAN_API_KEY:
            raise ValueError("❌ SHODAN_API_KEY missing")

        self.api = shodan.Shodan(SHODAN_API_KEY)


    @commands.command(name="shodan")
    async def shodan_search(self, ctx, ip):

        msg = await ctx.send("🔎 Searching Shodan...")

        try:
            result = await asyncio.to_thread(
                self.api.host,
                ip
            )

            embed = discord.Embed(
                title=f"🌐 Shodan: {ip}",
                color=discord.Color.blue()
            )

            embed.add_field(
                name="🏢 Organization",
                value=result.get("org", "Unknown"),
                inline=False
            )

            embed.add_field(
                name="🌍 Country",
                value=result.get("country_name", "Unknown"),
                inline=False
            )

            ports = result.get("ports", [])
            embed.add_field(
                name="🔌 Ports",
                value=", ".join(map(str, ports)) if ports else "None",
                inline=False
            )

            await msg.edit(embed=embed)

        except shodan.APIError as e:
            await msg.edit(
                content=f"❌ Shodan error: `{e}`"
            )


async def setup(bot):
    await bot.add_cog(ShodanCog(bot))