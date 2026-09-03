import os
import asyncio
import discord

from discord.ext import commands, tasks
from mcstatus import JavaServer


class MCStatusTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server = JavaServer.lookup("host.docker.internal:25565")
        self.last_state = None

        self.loop_mc_status.start()

    async def update_mc_status(self):
        channel_id = os.getenv("MC_STATUS_CHANNEL_ID")

        if not channel_id:
            print("❌ MC_STATUS_CHANNEL_ID is not set.")
            return

        channel = self.bot.get_channel(int(channel_id))

        if channel is None:
            try:
                channel = await self.bot.fetch_channel(int(channel_id))
            except discord.HTTPException as e:
                print(f"❌ Failed to fetch MC status channel: {e}")
                return

        try:
            self.server.status()
            state = "🟢│Online"

        except Exception:
            state = "🔴│Offline"

        # Don't edit Discord channel if nothing changed
        if state == self.last_state:
            return

        self.last_state = state

        try:
            await channel.edit(name=state)

        except discord.HTTPException as e:
            if e.status == 429:
                print("⚠️ Discord rate limited, retrying later.")
                await asyncio.sleep(60)
            else:
                print(f"❌ Failed to edit channel: {e}")

    @tasks.loop(seconds=60)
    async def loop_mc_status(self):
        await self.update_mc_status()

    @loop_mc_status.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()
        await self.update_mc_status()

    def cog_unload(self):
        self.loop_mc_status.cancel()


async def setup(bot):
    await bot.add_cog(MCStatusTask(bot))