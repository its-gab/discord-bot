import os
import asyncio
import discord

from discord.ext import commands, tasks
from mcstatus import JavaServer


class MinecraftStatusTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server = JavaServer.lookup("localhost:25565")
        self.last_state = None

        self.loop_minecraft_status.start()


    async def update_minecraft_status(self):
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
    async def loop_minecraft_status(self):
        await self.update_minecraft_status()


    @loop_minecraft_status.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()
        await self.update_minecraft_status()


async def setup(bot):
    await bot.add_cog(MinecraftStatusTask(bot))