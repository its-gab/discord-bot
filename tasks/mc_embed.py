import os
import discord
from discord import tasks

from config import STATE_FILE
from utils.save import load_json, save_json
from services.mc_embed import create_mc_embed

class MCEmbedTask:
    def __init__(self, bot):
        self.bot = bot

        try:
            self.loop_mc_embed.start()
            print("✅ MCEmbedTask started successfully")
        except Exception as e:
            print(f"❌ MCEmbedTask failed: {e}")

    @tasks.loop(seconds=60)
    async def loop_mc_embed(self):
        channel = await self.bot.fetch_channel(int(os.getenv("MC_INFO_CHANNEL_ID")))
        embed = create_mc_embed()

        state = load_json(STATE_FILE)
        message_id = state.get("mc_status_message_id")

        if not message_id:
            msg = await channel.send(embed=embed)
            state["mc_status_message_id"] = msg.id
            save_json(STATE_FILE, state)
            return

        try:
            msg = await channel.fetch_message(message_id)
            await msg.edit(embed=embed)

        except discord.NotFound:
            msg = await channel.send(embed=embed)
            state["mc_status_message_id"] = msg.id
            save_json(STATE_FILE, state)