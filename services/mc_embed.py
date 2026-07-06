import time
import discord
from mcstatus import JavaServer

from services.minecraft import mc_start_time

def create_mc_embed():
    server = JavaServer.lookup("localhost:25565")

    try:
        status = server.status()
        online = status.players.online
        max_players = status.players.max
        ping = round(status.latency)
        state = "🟢 Online"
        color = 0x00ff00
    except:
        online = 0
        max_players = 0
        ping = "N/A"
        state = "🔴 Offline"
        color = 0xff0000

    try:
        uptime_seconds = int(time.time() - mc_start_time)
        h = uptime_seconds // 3600
        m = (uptime_seconds % 3600) // 60
        uptime = f"{h}h {m}m"
    except:
        uptime = "N/A"

    embed = discord.Embed(
        title="📡 Minecraft Server Status",
        description="Live dashboard ⚡",
        color=color
    )

    embed.add_field(name="Status", value=state, inline=True)
    embed.add_field(name="Player", value=f"{online}/{max_players}", inline=True)
    embed.add_field(name="Ping", value=f"{ping} ms", inline=True)

    embed.add_field(name="Uptime", value=uptime, inline=True)
    embed.add_field(name="IP", value="localhost:25565", inline=True)
    embed.add_field(name="Update", value="every 60s", inline=True)

    embed.set_footer(text="MC Dashboard Bot 🤖")

    return embed