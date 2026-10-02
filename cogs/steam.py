import asyncio
import logging
import os

import discord
from discord.ext import commands, tasks

from config import STEAM_STATE_FILE
from services.steam import get_wishlist_discounts
from services.discounts_embed import create_steam_embed
from services.utils import save_json, load_json


logger = logging.getLogger(__name__)


class SteamWishlistTask(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.loop_wishlist_check.start()

    def cog_unload(self):
        self.loop_wishlist_check.cancel()

    async def update_wishlist(self):
        channel_id = os.getenv(
            "STEAM_WISHLIST_CHANNEL_ID"
        )

        steam_id = os.getenv(
            "STEAM_ID"
        )

        if not channel_id:
            raise RuntimeError(
                "STEAM_WISHLIST_CHANNEL_ID is not configured."
            )

        if not steam_id:
            raise RuntimeError(
                "STEAM_ID is not configured."
            )

        channel = self.bot.get_channel(
            int(channel_id)
        )

        if channel is None:
            channel = await self.bot.fetch_channel(
                int(channel_id)
            )

        state = load_json(
            STEAM_STATE_FILE
        )

        message_id = state.get(
            "wishlist_message_id"
        )

        logger.info(
            "Checking Steam wishlist..."
        )

        discounts = await asyncio.to_thread(
            get_wishlist_discounts,
            steam_id
        )

        embed = create_steam_embed(
            discounts
        )

        if message_id:
            try:
                message = await channel.fetch_message(
                    message_id
                )

                await message.edit(
                    content=None,
                    embed=embed
                )

                logger.info(
                    "Steam wishlist message updated."
                )

                return

            except discord.NotFound:
                logger.warning(
                    "Steam wishlist message no longer exists."
                )

        message = await channel.send(
            embed=embed
        )

        state["wishlist_message_id"] = message.id

        save_json(
            STEAM_STATE_FILE,
            state
        )

        logger.info(
            "Created new Steam wishlist message: %s",
            message.id
        )

    @tasks.loop(hours=6)
    async def loop_wishlist_check(self):
        try:
            await self.update_wishlist()

        except Exception:
            logger.exception(
                "Error while updating Steam wishlist."
            )

    @loop_wishlist_check.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

        logger.info(
            "Steam wishlist task is ready."
        )


async def setup(bot):
    await bot.add_cog(
        SteamWishlistTask(bot)
    )