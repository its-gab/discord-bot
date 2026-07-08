import time
from discord.ext import commands
from config import BOT_START_TIME
from utils.formatter import format_uptime

class General(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hello(self, ctx):
        await ctx.reply(f"Hello {ctx.author.mention}!👋",)
    
    @commands.command()
    async def say(self, ctx, *, msg):
        await ctx.send(msg)
    
    @commands.command()
    async def ping(self, ctx):
        message = await ctx.send("🏓 Ping...")
        latency = round(self.bot.latency * 1000)
        await message.edit(content=f"🏓 Pong! {latency}ms")
    
    @commands.command()
    async def uptime(self, ctx):
        bot_uptime = int(time.time() - BOT_START_TIME)
        await ctx.reply(f"Uptime: {format_uptime(bot_uptime)}")


# Setup
async def setup(bot):
    await bot.add_cog(General(bot))