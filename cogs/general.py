import time

import discord
from discord import app_commands
from discord.ext import commands

from services.permissions import allowed_channel
from services.utils import get_uptime


class General(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    @allowed_channel("COMMANDS_CHANNEL_ID")
    @app_commands.command(
        name="ping",
        description="Check if the bot is online."
    )
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)

        await interaction.response.send_message(
            f"🏓 Pong! `{latency}ms`"
        )

    @allowed_channel("COMMANDS_CHANNEL_ID")
    @app_commands.command(
        name="about",
        description="Get information about the bot."
    )
    async def about(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "I am a simple Discord bot written in Python by gab!"
        )

    @allowed_channel("COMMANDS_CHANNEL_ID")
    @app_commands.command(
        name="uptime",
        description="Check the bot's uptime."
    )
    async def uptime(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Bot has been running for {get_uptime(self.start_time)}!"
        )

    @allowed_channel("COMMANDS_CHANNEL_ID")
    @app_commands.command(
        name="stats",
        description="Check the bot's statistics."
    )
    async def stats(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Bot stats:\n"
            f"- Uptime: {get_uptime(self.start_time)}\n"
            f"- Latency: {round(self.bot.latency * 1000)}ms"
        )


async def setup(bot):
    await bot.add_cog(General(bot))