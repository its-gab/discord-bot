import os
import discord
from discord.ext import commands, tasks

from services.steam import check_steam_wishlist
from services.discounts_embed import create_steam_embed
from config import STATE_FILE
from utils.save import save_json, load_json

class SteamWishlistTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.loop_whishlist_check.start()

    @tasks.loop(hours=6)
    async def loop_whishlist_check(self):
        channel_id = int(os.getenv("STEAM_WISHLIST_CHANNEL_ID"))

        channel = self.bot.get_channel(channel_id)
        if channel is None:
            channel = await self.bot.fetch_channel(channel_id)

        state = load_json(STATE_FILE)
        message_id = state.get("steam_wishlist_message_id")

        discounts = await check_steam_wishlist()

        embed = create_steam_embed(discounts)

        if message_id:
            try:
                msg = await channel.fetch_message(message_id)
            except discord.NotFound:
                msg = await channel.send(embed=embed)
                state["steam_wishlist_message_id"] = msg.id
                save_json(STATE_FILE, state)
            else:
                await msg.edit(content=None, embed=embed)
        else:
            msg = await channel.send(embed=embed)
            state["steam_wishlist_message_id"] = msg.id
            save_json(STATE_FILE, state)


        
        
async def setup(bot):

    await bot.add_cog(SteamWishlistTask(bot))