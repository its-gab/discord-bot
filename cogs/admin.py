from discord.ext import commands

class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def clear(self, ctx, amount: int = 5):
        await ctx.message.delete()
        await ctx.channel.purge(limit=amount + 1)


# Setup
async def setup(bot):
    await bot.add_cog(Admin(bot))