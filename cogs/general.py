from discord.ext import commands

class General(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hello(self, ctx):
        await ctx.reply(f"Hello {ctx.author.mention}!👋",)

    @commands.command()
    async def ping(self, ctx):
        message = await ctx.send("🏓 Ping...")
        latency = round(self.bot.latency * 1000)
        await message.edit(content=f"🏓 Pong! {latency}ms")


# Setup
async def setup(bot):
    await bot.add_cog(General(bot))