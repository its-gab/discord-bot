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


    async def update_mc_embed(self):
        channel_id = int(os.getenv("MC_INFO_CHANNEL_ID"))

        channel = self.bot.get_channel(channel_id)
        if channel is None:
            channel = await self.bot.fetch_channel(channel_id)

        embed = create_mc_embed()

        state = load_json(STATE_FILE)
        message_id = state.get("mc_status_message_id")


        if message_id:
            try:
                msg = await channel.fetch_message(message_id)
                await msg.edit(embed=embed)
                return

            except discord.NotFound:
                pass


        msg = await channel.send(embed=embed)

        state["mc_status_message_id"] = msg.id
        save_json(STATE_FILE, state)



    @tasks.loop(seconds=60)
    async def loop_mc_embed(self):
        await self.update_mc_embed()


    @loop_mc_embed.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()
        await self.update_mc_embed()



async def setup(bot):
    await bot.add_cog(MCEmbedTask(bot))