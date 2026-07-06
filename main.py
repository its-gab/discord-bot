import asyncio

from config import bot, DS_TOKEN

EXTENSIONS = (
    "cogs.admin",
    "cogs.events",
    "cogs.general",
    "cogs.minecraft",
    "cogs.sensors",
    "cogs.test",
    "cogs.tv",
)

async def main():
    async with bot:
        print("📜 Loading modules...")
        for extension in EXTENSIONS:
            try:
                await bot.load_extension(extension)
                print(f"✅ Loaded: {extension}")
            except Exception as e:
                print(f"❌ Error loading module {extension}: {e}")
        print("✅ Modules loaded!")

        print("📦 Loading tasks...")
        await bot.load_extension("cogs.tasks")
        print("✅ Tasks loaded!")

        print("🚀 Bot starting...")
        await bot.start(DS_TOKEN)

asyncio.run(main())