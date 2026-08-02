import os
import discord
import asyncio
from discord.ext import commands, tasks

from services.steam import get_wishlist_discounts
from services.discounts_embed import create_steam_embed
from config import STATE_FILE
from utils.save import save_json, load_json

class SteamWishlistTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.loop_wishlist_check.start()

    async def update_wishlist(self):
        channel_id = int(os.getenv("STEAM_WISHLIST_CHANNEL_ID"))
        steam_id = os.getenv("STEAM_ID")

        channel = self.bot.get_channel(channel_id)
        if channel is None:
            channel = await self.bot.fetch_channel(channel_id)

        state = load_json(STATE_FILE)
        message_id = state.get("steam_wishlist_message_id")

        discounts = await asyncio.to_thread(
            get_wishlist_discounts,
            steam_id
        )

        embed = create_steam_embed(discounts)

        if message_id:
            try:
                msg = await channel.fetch_message(message_id)
                await msg.edit(content=None, embed=embed)

            except discord.NotFound:
                msg = await channel.send(embed=embed)
                state["steam_wishlist_message_id"] = msg.id
                save_json(STATE_FILE, state)

        else:
            msg = await channel.send(embed=embed)
            state["steam_wishlist_message_id"] = msg.id
            save_json(STATE_FILE, state)


    @tasks.loop(hours=6)
    async def loop_wishlist_check(self):
        await self.update_wishlist()


    @loop_wishlist_check.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()
        await self.update_wishlist()
        
async def setup(bot):
    await bot.add_cog(SteamWishlistTask(bot))