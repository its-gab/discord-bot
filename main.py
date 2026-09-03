import asyncio
import signal

from config import bot, DS_TOKEN
from services.minecraft import remove_docker


COGS = (
    "cogs.admin",
    "cogs.camera",
    "cogs.events",
    "cogs.fuel",
    "cogs.general",
    "cogs.ip",
    "cogs.minecraft",
    "cogs.sensors",
    "cogs.server",
    "cogs.shodan_api",
    "cogs.test",
    "cogs.tv",
)

TASKS = (
    "tasks.mc_embed",
    "tasks.mc_status",
    "tasks.steam_wishlist",
)


async def main():
    loop = asyncio.get_running_loop()

    shutting_down = False

    async def shutdown():
        nonlocal shutting_down

        if shutting_down:
            return

        shutting_down = True

        print("🛑 Shutdown signal received.")
        print("🔴 Stopping Minecraft server...")

        try:
            result = await asyncio.to_thread(remove_docker)
            print(result)
        except Exception as e:
            print(f"❌ Failed to stop Minecraft: {e}")
            
        print("👋 Closing Discord bot...")
        await bot.close()

    def handle_shutdown():
        if not shutting_down:
            asyncio.create_task(shutdown())

    try:
        loop.add_signal_handler(signal.SIGTERM, handle_shutdown)
        loop.add_signal_handler(signal.SIGINT, handle_shutdown)
    except NotImplementedError:
        # Necessario su alcuni sistemi
        signal.signal(
            signal.SIGTERM,
            lambda *_: asyncio.create_task(shutdown())
        )
        signal.signal(
            signal.SIGINT,
            lambda *_: asyncio.create_task(shutdown())
        )


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