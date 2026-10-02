import asyncio
import logging
import os
import time

import discord
from discord.ext import commands


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)


TOKEN = os.getenv("DISCORD_TOKEN")


intents = discord.Intents.default()
intents.members = True


bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

bot.start_time = time.time()


async def load_cogs():
    logger.info("Loading cogs...")

    for filename in os.listdir("./cogs"):
        if not filename.endswith(".py"):
            continue

        if filename.startswith("_"):
            continue

        try:
            await bot.load_extension(
                f"cogs.{filename[:-3]}"
            )

            logger.info(
                "Loaded cog: %s",
                filename
            )

        except Exception:
            logger.exception(
                "Failed to load cog: %s",
                filename
            )


@bot.event
async def on_ready():
    await bot.tree.sync()

    logger.info(
        "Logged in as %s",
        bot.user
    )


async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())