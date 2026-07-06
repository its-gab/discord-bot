from discord.ext import commands
from services.samsung_tv import get_tv_status, power_tv


class TV(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def tv(self, ctx, action: str):
        action = action.lower()

        if action == "status":
            status = get_tv_status()

            if status is None:
                await ctx.reply("❌ TV status unknown.")
            else:
                state = "on" if status else "off"
                await ctx.reply(f"📺 TV is {state}")
            return

        message = power_tv(action)
        await ctx.reply(message)


async def setup(bot):
    await bot.add_cog(TV(bot))