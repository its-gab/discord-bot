import os

import discord
from discord import app_commands


def allowed_channel(*env_names: str):
    async def predicate(interaction: discord.Interaction) -> bool:
        allowed_channels = {
            int(os.getenv(name))
            for name in env_names
        }

        if interaction.channel_id in allowed_channels:
            return True

        await interaction.response.send_message(
            "❌ You cannot use this command here.",
            ephemeral=True
        )

        return False

    return app_commands.check(predicate)


def owner_only():
    async def predicate(interaction: discord.Interaction) -> bool:
        owner_id = int(os.getenv("OWNER_ID"))

        if interaction.user.id == owner_id:
            return True

        await interaction.response.send_message(
            "❌ Only the owner can use this command.",
            ephemeral=True
        )

        return False

    return app_commands.check(predicate)