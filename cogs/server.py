import discord
from discord import app_commands
from discord.ext import commands

from services.server import (
    get_system_uptime,
    get_cpu_usage,
    get_cpu_temp,
    get_ram,
    get_disk,
    get_local_ip,
    docker_containers
)
from services.utils import format_uptime
from services.permissions import allowed_channel, owner_only


class Server(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    server_group = app_commands.Group(
        name="server",
        description="Raspberry Pi server information."
    )

    @server_group.command(
        name="uptime",
        description="Show the Raspberry Pi system uptime."
    )
    @allowed_channel("ADMIN_COMMANDS_CHANNEL_ID")
    @owner_only()
    async def server_uptime(self, interaction: discord.Interaction):
        uptime = format_uptime(get_system_uptime())

        await interaction.response.send_message(
            f"⏱️ System uptime: **{uptime}**"
        )

    @server_group.command(
        name="info",
        description="Show Raspberry Pi information."
    )
    @allowed_channel("ADMIN_COMMANDS_CHANNEL_ID")
    @owner_only()
    async def server_info(self, interaction: discord.Interaction):

        cpu = get_cpu_usage()
        cpu_temp = get_cpu_temp()
        ram = get_ram()
        disk = get_disk()
        ip = get_local_ip()
        uptime = format_uptime(get_system_uptime())

        embed = discord.Embed(
            title="🖥️ Raspberry Pi Information",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="🧠 CPU",
            value=f"Usage: **{cpu}%**",
            inline=True
        )

        embed.add_field(
            name="🌡️ CPU Temp",
            value=f"**{cpu_temp:.1f}°C**" if cpu_temp else "N/A",
            inline=True
        )

        embed.add_field(
            name="⏱️ Uptime",
            value=f"**{uptime}**",
            inline=True
        )

        embed.add_field(
            name="💾 RAM",
            value=(
                f"{ram['used']/1024**3:.2f} / "
                f"{ram['total']/1024**3:.2f} GB\n"
                f"({ram['percent']}%)"
            ),
            inline=True
        )

        embed.add_field(
            name="📀 Disk",
            value=(
                f"{disk['used']/1024**3:.2f} / "
                f"{disk['total']/1024**3:.2f} GB\n"
                f"({disk['percent']}%)"
            ),
            inline=True
        )

        embed.add_field(
            name="🌐 Local IP",
            value=f"`{ip}`",
            inline=True
        )

        embed.set_footer(text="Raspberry Pi Monitor")

        await interaction.response.send_message(embed=embed)

    @server_group.command(
        name="docker",
        description="Show running Docker containers."
    )
    @allowed_channel("ADMIN_COMMANDS_CHANNEL_ID")
    @owner_only()
    async def server_docker(self, interaction: discord.Interaction):
        containers = docker_containers()

        if containers is None:
            await interaction.response.send_message(
                "❌ Unable to connect to Docker.",
                ephemeral=True
            )
            return

        if len(containers) == 0:
            await interaction.response.send_message(
                "📦 No running containers."
            )
            return

        embed = discord.Embed(
            title="📦 Docker Containers",
            description=f"**{len(containers)} containers running**",
            color=discord.Color.green()
        )

        for name, status in containers:

            status_lower = status.lower()

            if "(healthy)" in status_lower:
                status_text = status.replace(
                    "(healthy)",
                    ""
                ).strip()

                status_text += " · `Healthy`"

            else:
                status_text = status

            embed.add_field(
                name=f"🟢 {name}",
                value=f"`{status_text}`",
                inline=False
            )

        embed.set_footer(
            text="Docker • Raspberry Pi"
        )

        await interaction.response.send_message(
            embed=embed
        )


async def setup(bot):
    await bot.add_cog(Server(bot))