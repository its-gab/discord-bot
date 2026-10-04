import logging
import os

import discord
from discord import app_commands

logger = logging.getLogger(__name__)


def allowed_channel(*env_names: str):
    async def predicate(interaction: discord.Interaction) -> bool:
        allowed_channels = set()

        for env_name in env_names:
            value = os.getenv(env_name)

            if not value:
                logger.error(
                    "Channel ID environment variable '%s' is not configured.",
                    env_name
                )
                continue

            try:
                channel_id = int(value)
                allowed_channels.add(channel_id)

            except ValueError:
                logger.error(
                    "Invalid channel ID in '%s': %r",
                    env_name,
                    value
                )

        if interaction.channel_id in allowed_channels:
            logger.debug(
                "Channel check passed for /%s | channel=%s",
                interaction.command.name if interaction.command else "unknown",
                interaction.channel_id
            )
            return True

        logger.warning(
            "Channel check failed for /%s | user=%s (%s) | "
            "channel=%s | allowed=%s",
            interaction.command.name if interaction.command else "unknown",
            interaction.user.id,
            interaction.user,
            interaction.channel_id,
            sorted(allowed_channels)
        )

        await interaction.response.send_message(
            "❌ You cannot use this command here.",
            ephemeral=True
        )

        return False

    return app_commands.check(predicate)


def owner_only():
    async def predicate(interaction: discord.Interaction) -> bool:
        owner_id = os.getenv("OWNER_ID")

        if not owner_id:
            logger.error(
                "OWNER_ID is not configured."
            )

            await interaction.response.send_message(
                "❌ Bot owner is not configured.",
                ephemeral=True
            )

            return False

        try:
            owner_id = int(owner_id)

        except ValueError:
            logger.error(
                "Invalid OWNER_ID: %r",
                owner_id
            )

            await interaction.response.send_message(
                "❌ Bot owner configuration is invalid.",
                ephemeral=True
            )

            return False

        if interaction.user.id == owner_id:
            logger.debug(
                "Owner check passed for /%s | user=%s",
                interaction.command.name if interaction.command else "unknown",
                interaction.user.id
            )
            return True

        logger.warning(
            "Owner check failed for /%s | user=%s (%s) | expected_owner=%s",
            interaction.command.name if interaction.command else "unknown",
            interaction.user.id,
            interaction.user,
            owner_id
        )

        await interaction.response.send_message(
            "❌ Only the owner can use this command.",
            ephemeral=True
        )

        return False

    return app_commands.check(predicate)