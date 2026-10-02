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

DISABLED_FILE = ".disabled"


intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

bot.start_time = time.time()


def load_disabled_cogs():
    if not os.path.exists(DISABLED_FILE):
        return set()

    with open(DISABLED_FILE, "r", encoding="utf-8") as file:
        return {
            line.strip().lower()
            for line in file
            if line.strip() and not line.startswith("#")
        }


async def load_cogs():
    logger.info("Loading cogs...")

    disabled_cogs = load_disabled_cogs()

    if disabled_cogs:
        logger.info(
            "Disabled cogs: %s",
            ", ".join(sorted(disabled_cogs))
        )

    for filename in os.listdir("./cogs"):
        if not filename.endswith(".py"):
            continue

        if filename.startswith("_"):
            continue

        cog_name = filename[:-3].lower()

        if cog_name in disabled_cogs:
            logger.info("Skipped disabled cog: %s", filename)
            continue

        try:
            await bot.load_extension(f"cogs.{cog_name}")
            logger.info("Loaded cog: %s", filename)
        except Exception:
            logger.exception("Failed to load cog: %s", filename)


@bot.event
async def on_ready():
    await bot.tree.sync()
    logger.info("Logged in as %s", bot.user)


async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())