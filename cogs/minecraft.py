from discord.ext import commands

from services.minecraft import start_server, stop_server, restart_server

class Minecraft(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def mc(self, ctx, action: str = None):
        if action is None:
            await ctx.reply("❌ No argument provided. Use: !mc start - !mc stop - !mc status")
            return

        action = action.lower()

        if action == "start":
            await ctx.reply(start_server())
        elif action == "stop":
            await ctx.reply(stop_server())
        elif action == "status":
            await ctx.reply("Checking Minecraft server status...")
        else:
            await ctx.reply("❌ Invalid argument. Use: !mc start - !mc stop - !mc status")


# Setup
async def setup(bot):
    await bot.add_cog(Minecraft(bot))