import time
from datetime import datetime

import discord
from mcstatus import JavaServer

from services.docker import (
    container_exists,
    container_running,
    docker_command,
)

from services.utils import format_uptime


MC_CONTAINER = "minecraft"
MC_ADDRESS = "host.docker.internal:25565"


def get_container_uptime():
    if not container_exists(MC_CONTAINER):
        return None

    if not container_running(MC_CONTAINER):
        return None

    result = docker_command(
        "inspect",
        "-f",
        "{{.State.StartedAt}}",
        MC_CONTAINER
    )

    if result is None or result.returncode != 0:
        return None

    try:
        started_at = result.stdout.strip()

        start_time = datetime.fromisoformat(
            started_at.replace("Z", "+00:00")
        )

        uptime_seconds = int(
            time.time() - start_time.timestamp()
        )

        return format_uptime(max(0, uptime_seconds))

    except (ValueError, TypeError):
        return None


def create_mc_embed():

    server = JavaServer.lookup(MC_ADDRESS)

    try:
        status = server.status()

        online = status.players.online
        max_players = status.players.max
        ping = round(status.latency)

        state = "🟢 Online"
        color = 0x00ff00

    except Exception:
        # Minecraft server is offline or unreachable.
        online = 0
        max_players = 0
        ping = "N/A"

        state = "🔴 Offline"
        color = 0xff0000

    uptime = get_container_uptime()

    if uptime is None:
        uptime = "N/A"

    embed = discord.Embed(
        title="📡 Minecraft Server Status",
        description="Live dashboard ⚡",
        color=color
    )

    embed.add_field(
        name="Status",
        value=state,
        inline=True
    )

    embed.add_field(
        name="Players",
        value=f"{online}/{max_players}",
        inline=True
    )

    embed.add_field(
        name="Ping",
        value=f"{ping} ms",
        inline=True
    )

    embed.add_field(
        name="Uptime",
        value=uptime,
        inline=True
    )

    embed.add_field(
        name="IP",
        value="localhost:25565",
        inline=True
    )

    embed.add_field(
        name="Update",
        value="every 60s",
        inline=True
    )

    embed.set_footer(
        text="MC Dashboard Bot 🤖"
    )

    return embed