import os
import importlib

TASKS_PACKAGE = "tasks"

class TaskManager:
    def __init__(self, bot):
        self.bot = bot
        self.tasks = []

    async def load_tasks(self):
        for file in os.listdir("./tasks"):
            if not file.endswith(".py") or file.startswith("_"):
                continue

            module_name = f"{TASKS_PACKAGE}.{file[:-3]}"

            module = importlib.import_module(module_name)

            for attr_name in dir(module):
                attr = getattr(module, attr_name)

                if hasattr(attr, "start"):
                    try:
                        instance = attr(self.bot)
                        self.tasks.append(instance)
                        print(f"✅ Task loaded: {attr_name}")
                    except Exception as e:
                        print(f"❌ Error loading task {attr_name}: {e}")