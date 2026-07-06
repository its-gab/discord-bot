from discord.ext import commands
from task_manager import TaskManager


class TasksCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.task_manager = TaskManager(bot)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.task_manager.load_tasks()


async def setup(bot):
    await bot.add_cog(TasksCog(bot))