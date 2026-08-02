import os
import asyncio
import discord

from discord.ext import commands, tasks
from mcstatus import JavaServer


class MCStatusTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server = JavaServer.lookup("localhost:25565")
        self.last_state = None

        self.loop_mc_status.start()


    async def update_mc_status(self):
        channel_id = int(os.getenv("MC_STATUS_CHANNEL_ID"))

        channel = self.bot.get_channel(channel_id)
        if channel is None:
            channel = await self.bot.fetch_channel(channel_id)

        try:
            self.server.status()
            state = "🟢│Online"

        except Exception:
            state = "🔴│Offline"


        if state != self.last_state:
            self.last_state = state

            try:
                await channel.edit(name=state)

            except discord.HTTPException as e:
                if e.status == 429:
                    print("⚠️ Rate limited, retry later")
                    await asyncio.sleep(60)


    @tasks.loop(seconds=60)
    async def loop_mc_status(self):
        await self.update_mc_status()


    @loop_mc_status.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()
        await self.update_mc_status()


async def setup(bot):
    await bot.add_cog(MCStatusTask(bot))