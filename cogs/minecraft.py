import asyncio
import logging
import os

import discord
from discord import app_commands
from discord.ext import commands, tasks
from mcstatus import JavaServer

from config import MC_STATE_FILE
from services.utils import load_json, save_json
from services.mc_embed import create_mc_embed

from services.minecraft import (
    start_server,
    stop_server,
    restart_server,
    remove_server,
    server_status,
)

from services.permissions import allowed_channel, owner_only


logger = logging.getLogger(__name__)


class Minecraft(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.server = JavaServer.lookup(
            "host.docker.internal:25565"
        )

        self.last_mc_state = None

        self.mc_loop.start()

    def cog_unload(self):
        self.mc_loop.cancel()

    # Minecraft Status + Embed Loop

    @tasks.loop(seconds=60)
    async def mc_loop(self):

        await self.update_mc_status()
        await self.update_mc_embed()

    @mc_loop.before_loop
    async def before_mc_loop(self):
        await self.bot.wait_until_ready()

        logger.info(
            "Minecraft status and embed task is ready."
        )

        # Update immediately instead of waiting 60 seconds
        await self.update_mc_status()
        await self.update_mc_embed()

    # Minecraft Channel Status

    async def update_mc_status(self):
        channel_id = os.getenv("MINECRAFT_INFO_CHANNEL_ID")

        if not channel_id:
            logger.error(
                "MINECRAFT_INFO_CHANNEL_ID is not configured."
            )
            return

        try:
            channel = self.bot.get_channel(
                int(channel_id)
            )

            if channel is None:
                channel = await self.bot.fetch_channel(
                    int(channel_id)
                )

        except discord.HTTPException:
            logger.exception(
                "Failed to fetch Minecraft status channel."
            )
            return

        try:
            self.server.status()
            state = "🟢│Online"

        except Exception:
            state = "🔴│Offline"

        # Don't edit if nothing changed
        if state == self.last_mc_state:
            return

        try:
            await channel.edit(name=state)

            self.last_mc_state = state

            logger.info(
                "Minecraft status channel updated: %s",
                state
            )

        except discord.Forbidden:
            logger.error(
                "Missing 'Manage Channels' permission "
                "for Minecraft info channel."
            )

        except discord.HTTPException as e:

            if e.status == 429:
                logger.warning(
                    "Discord rate limited while updating "
                    "Minecraft status channel."
                )
            else:
                logger.exception(
                    "Failed to update Minecraft status channel."
                )

    # Minecraft Embed

    async def update_mc_embed(self):

        channel_id = os.getenv(
            "MINECRAFT_INFO_CHANNEL_ID"
        )

        if not channel_id:
            logger.error(
                "MINECRAFT_INFO_CHANNEL_ID is not configured."
            )
            return

        try:
            channel = self.bot.get_channel(
                int(channel_id)
            )

            if channel is None:
                channel = await self.bot.fetch_channel(
                    int(channel_id)
                )

            embed = create_mc_embed()

            state = load_json(MC_STATE_FILE)
            message_id = state.get(
                "mc_status_message_id"
            )

            # No existing message
            if not message_id:

                message = await channel.send(
                    embed=embed
                )

                state["mc_status_message_id"] = (
                    message.id
                )

                save_json(
                    MC_STATE_FILE,
                    state
                )

                logger.info(
                    "Created Minecraft status message: %s",
                    message.id
                )

                return

            try:

                message = await channel.fetch_message(
                    message_id
                )

                await message.edit(
                    embed=embed
                )

            except discord.NotFound:

                logger.warning(
                    "Minecraft status message no longer exists. "
                    "Creating a new one."
                )

                message = await channel.send(
                    embed=embed
                )

                state["mc_status_message_id"] = (
                    message.id
                )

                save_json(
                    MC_STATE_FILE,
                    state
                )

        except discord.Forbidden:

            logger.error(
                "Missing permissions in Minecraft info channel."
            )

        except discord.HTTPException:

            logger.exception(
                "Discord API error while updating "
                "Minecraft embed."
            )

        except Exception:

            logger.exception(
                "Unexpected error while updating "
                "Minecraft embed."
            )

    # Minecraft Commands

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
    async def minecraft_start(
        self,
        interaction: discord.Interaction
    ):

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
    async def minecraft_stop(
        self,
        interaction: discord.Interaction
    ):

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
    async def minecraft_restart(
        self,
        interaction: discord.Interaction
    ):

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
    async def minecraft_status(
        self,
        interaction: discord.Interaction
    ):

        status = server_status()

        if status == "online":
            message = (
                "🟢 Minecraft server is online."
            )
        elif status == "offline":
            message = (
                "🔴 Minecraft server is offline."
            )
        else:
            message = (
                "⚪ Minecraft server has not "
                "been created yet."
            )
        await interaction.response.send_message(
            message
        )

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