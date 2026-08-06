import discord
from discord.ext import commands
import shodan
import os

SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")


class ShodanCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.api = shodan.Shodan(SHODAN_API_KEY)


    @commands.command()
    async def shodan(self, ctx, *, query):
        try:
            results = self.api.search(query)

            if results["total"] == 0:
                await ctx.reply("❌ No results found")
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

                embed.add_field(
                    name=f"{ip}:{port}",
                    value=f"🏢 {org}",
                    inline=False
                )


            await ctx.reply(embed=embed)


        except shodan.APIError as e:
            await ctx.reply(f"❌ Shodan error: {e}")


async def setup(bot):
    await bot.add_cog(ShodanCog(bot))