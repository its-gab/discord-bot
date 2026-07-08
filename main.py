import asyncio

from config import bot, DS_TOKEN

COGS = (
    "cogs.admin",
    "cogs.events",
    "cogs.general",
    "cogs.minecraft",
    "cogs.sensors",
    "cogs.server"
    "cogs.test",
    "cogs.tv",
)

TASKS = (
    "tasks.mc_embed",
    "tasks.mc_status",
)


async def main():
    async with bot:
        print("📜 Loading modules...")
        for cog in COGS:
            try:
                await bot.load_extension(cog)
                print(f"✅ Loaded {cog}")
            except Exception as e:
                print(f"❌ Error loading {cog}: {e}")
        print("✅ Modules loaded!")

        print("📦 Loading tasks...")

        for task in TASKS:
            try:
                await bot.load_extension(task)
                print(f"✅ Loaded {task}")
            except Exception as e:
                print(f"❌ Error loading {task}: {e}")
        print("✅ Tasks loaded!")

        print("🚀 Bot starting...")
        await bot.start(DS_TOKEN)

asyncio.run(main())