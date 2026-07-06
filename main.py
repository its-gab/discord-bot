import asyncio

from config import bot, DS_TOKEN

EXTENSIONS = (
    "cogs.events",
)

async def main():
    async with bot:
        for extension in EXTENSIONS:
            await bot.load_extension(extension)

        await bot.start(DS_TOKEN)

asyncio.run(main())