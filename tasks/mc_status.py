import os
import asyncio
import discord
from discord.ext import tasks
from mcstatus import JavaServer


class MCStatusTask:
    def __init__(self, bot):
        self.bot = bot
        self.server = JavaServer.lookup("localhost:25565")
        self.last_state = None

        try:
            self.loop_mc_status.start()
            print("✅ MCStatusTask started successfully")
        except Exception as e:
            print(f"❌ MCStatusTask failed: {e}")

    @tasks.loop(seconds=60)
    async def loop_mc_status(self):

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
                    print("Rate limited, retry later")
                    await asyncio.sleep(60)