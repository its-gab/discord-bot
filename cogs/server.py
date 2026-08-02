import discord
from discord.ext import commands
from services.server import (
    get_system_uptime,
    reboot,
    get_cpu_usage,
    get_cpu_temp,
    get_ram,
    get_disk,
    get_local_ip,
    docker_containers
)
from utils.formatter import format_uptime

class Server(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def server(self, ctx, action: str = None):
        if action is None:
            await ctx.reply("❌ No argument provided!")
            return

        action = action.lower()

        if action == "uptime":
            await ctx.reply(f"System uptime: {format_uptime(get_system_uptime())}")
        elif action == "info":
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

            await ctx.reply(embed=embed, mention_author=False)
        elif action == "docker":
            containers = docker_containers()

            if containers is None:
                await ctx.reply("❌ Docker not installed")
                return

            if len(containers) == 0:
                await ctx.reply("📦 No running containers")
                return

            text = "📦 **Running containers**\n\n"

            for name, status in containers:
                text += f"🟢 **{name}**\n{status}\n\n"

            await ctx.reply(text)
    

async def setup(bot):
    await bot.add_cog(Server(bot))