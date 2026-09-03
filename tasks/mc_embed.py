import os
import discord
from discord.ext import commands, tasks

from config import STATE_FILE
from utils.save import load_json, save_json
from services.mc_embed import create_mc_embed


class MCEmbedTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.loop_mc_embed.start()

    def cog_unload(self):
        self.loop_mc_embed.cancel()

    @tasks.loop(seconds=60)
    async def loop_mc_embed(self):
        channel_id = os.getenv("MC_INFO_CHANNEL_ID")

        if not channel_id:
            print("❌ MC_INFO_CHANNEL_ID is not set.")
            return

        channel = await self.bot.fetch_channel(int(channel_id))

        embed = create_mc_embed()

        state = load_json(STATE_FILE)
        message_id = state.get("mc_status_message_id")

        # No existing message
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

    @loop_mc_embed.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(MCEmbedTask(bot))