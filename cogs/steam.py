from discord.ext import commands

class Steam(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def steam(self, ctx, action: str = None):
        if action == None:
            await ctx.send("Please specify an action. Available actions: `wishlist`")
        


async def setup(bot):
    await bot.add_cog(Steam(bot))