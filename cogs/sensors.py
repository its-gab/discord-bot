import discord
from discord.ext import commands
from services.dht11 import get_sensor_data


class Sensors(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def temp(self, ctx):
        data = get_sensor_data()

        temp = data["temp"]
        hum = data["hum"]

        if temp is None:
            await ctx.send("⚠️ Sensor not ready")
            return

        embed = discord.Embed(
            title="House Sensor",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )

        embed.add_field(name="🌡️ Temperature", value=f"{temp:.1f} °C", inline=True)
        embed.add_field(name="💧 Humidity", value=f"{hum:.1f} %", inline=True)

        if temp < 18:
            status = "❄️ Cold"
        elif temp < 26:
            status = "🙂 Normal"
        else:
            status = "🔥 Hot"

        embed.add_field(name="📊 Status", value=status, inline=False)

        embed.set_footer(text="Raspberry Pi Temperature Sensor")
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/728/728093.png")

        await ctx.reply(embed=embed, mention_author=False)


async def setup(bot):
    await bot.add_cog(Sensors(bot))