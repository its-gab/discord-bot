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
    async def shodan_search(self, ctx, *, query):

        msg = await ctx.send("🔎 Searching Shodan...")

        try:
            results = await asyncio.to_thread(
                self.api.search,
                query
            )

            if results["total"] == 0:
                await msg.edit(content="❌ No results found")
                return


            embed = discord.Embed(
                title=f"🔎 Shodan: {query}",
                description=f"Results found: {results['total']}",
                color=discord.Color.blue()
            )


            for result in results["matches"][:5]:

                ip = result.get("ip_str", "N/A")
                port = result.get("port", "N/A")
                org = result.get("org", "Unknown")
                country = result.get("location", {}).get(
                    "country_name",
                    "Unknown"
                )

                embed.add_field(
                    name=f"🌐 {ip}:{port}",
                    value=(
                        f"🏢 {org}\n"
                        f"🌍 {country}"
                    ),
                    inline=False
                )


            await msg.edit(embed=embed)


        except shodan.APIError as e:
            await msg.edit(
                content=f"❌ Shodan error: `{e}`"
            )


async def setup(bot):
    await bot.add_cog(ShodanCog(bot))