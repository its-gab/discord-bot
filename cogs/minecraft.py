import discord
from discord import app_commands
from discord.ext import commands

from services.minecraft import (
    start_server,
    stop_server,
    restart_server,
    remove_server,
    server_status,
)
from services.permissions import allowed_channel, owner_only


class Minecraft(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    minecraft_group = app_commands.Group(
        name="minecraft",
        description="Manage the Minecraft server."
    )

    @minecraft_group.command(
        name="start",
        description="Start the Minecraft server."
    )
    @allowed_channel("MINECRAFT_COMMANDS_CHANNEL_ID")
    @owner_only()
    async def minecraft_start(self, interaction: discord.Interaction):
        success, error = start_server()

        if success:
            await interaction.response.send_message(
                "🟢 Minecraft server started."
            )
        else:
            await interaction.response.send_message(
                f"❌ {error}",
                ephemeral=True
            )

    @minecraft_group.command(
        name="stop",
        description="Stop the Minecraft server."
    )
    @allowed_channel("MINECRAFT_COMMANDS_CHANNEL_ID")
    @owner_only()
    async def minecraft_stop(self, interaction: discord.Interaction):
        success, error = stop_server()

        if success:
            await interaction.response.send_message(
                "🔴 Minecraft server stopped."
            )
        else:
            await interaction.response.send_message(
                f"❌ {error}",
                ephemeral=True
            )

    @minecraft_group.command(
        name="restart",
        description="Restart the Minecraft server."
    )
    @allowed_channel("MINECRAFT_COMMANDS_CHANNEL_ID")
    @owner_only()
    async def minecraft_restart(self, interaction: discord.Interaction):
        success, error = restart_server()

        if success:
            await interaction.response.send_message(
                "🔄 Minecraft server restarted."
            )
        else:
            await interaction.response.send_message(
                f"❌ {error}",
                ephemeral=True
            )

    @minecraft_group.command(
        name="status",
        description="Check the Minecraft server status."
    )
    @allowed_channel("MINECRAFT_COMMANDS_CHANNEL_ID")
    async def minecraft_status(self, interaction: discord.Interaction):
        status = server_status()

        if status == "online":
            message = "🟢 Minecraft server is online."

        elif status == "offline":
            message = "🔴 Minecraft server is offline."

        else:
            message = "⚪ Minecraft server has not been created yet."

        await interaction.response.send_message(message)

    @minecraft_group.command(
        name="remove",
        description="Remove the Minecraft Docker container."
    )
    @allowed_channel("MINECRAFT_COMMANDS_CHANNEL_ID")
    @owner_only()
    async def minecraft_remove(
        self,
        interaction: discord.Interaction
    ):
        success, error = remove_server()

        if success:
            await interaction.response.send_message(
                "🗑️ Minecraft container removed."
            )
        else:
            await interaction.response.send_message(
                f"❌ {error}",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Minecraft(bot))