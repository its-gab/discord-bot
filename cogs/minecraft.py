import asyncio

from discord.ext import commands

from services.minecraft import (
    start_server,
    stop_server,
    restart_server,
    server_status,
    accept_eula
)


class Minecraft(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def mc(self, ctx, action: str = None):
        if action is None:
            await ctx.reply(
                "❌ No argument provided.\n"
                "Use: `!mc start` - `!mc stop` - `!mc restart` - "
                "`!mc eula` - `!mc status`"
            )
            return
            
        action = action.lower()

        if action == "start":
            message = await ctx.reply(
                "⏳ Starting Minecraft server..."
            )

            result = await asyncio.to_thread(start_server)
            await message.edit(content=result)

        elif action == "stop":
            message = await ctx.reply(
                "⏳ Stopping Minecraft server..."
            )

            result = await asyncio.to_thread(stop_server)
            await message.edit(content=result)

        elif action == "restart":
            message = await ctx.reply(
                "⏳ Restarting Minecraft server..."
            )

            result = await asyncio.to_thread(restart_server)
            await message.edit(content=result)

        elif action == "status":
            result = await asyncio.to_thread(server_status)
            await ctx.reply(result)

        else:

            await ctx.reply(
                "❌ Invalid argument.\n"
                "Use: `!mc start` - `!mc stop` - `!mc restart` - "
                "`!mc eula` - `!mc status`"
            )


async def setup(bot):
    await bot.add_cog(Minecraft(bot))