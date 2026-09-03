import time
import discord

from mcstatus import JavaServer

from utils.formatter import format_uptime
from services.minecraft import mc_start_time


MC_ADDRESS = "host.docker.internal:25565"


def create_mc_embed():

    server = JavaServer.lookup(MC_ADDRESS)

    try:
        status = server.status()

        online = status.players.online
        max_players = status.players.max
        ping = round(status.latency)

        state = "🟢 Online"
        color = 0x00ff00

    except Exception as e:

        print(f"❌ Minecraft status error: {e}")

        online = 0
        max_players = 0
        ping = "N/A"

        state = "🔴 Offline"
        color = 0xff0000

    # Uptime
    if mc_start_time is not None:

        uptime_seconds = int(time.time() - mc_start_time)
        uptime = format_uptime(uptime_seconds)

    else:
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