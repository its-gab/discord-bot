import asyncio
import logging

import discord
from discord import app_commands
from discord.ext import commands

from services.dht11 import get_sensor_data
from services.permissions import allowed_channel


logger = logging.getLogger(__name__)


class Sensors(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="temp",
        description="Show the current temperature and humidity."
    )
    @allowed_channel("COMMANDS_CHANNEL_ID")
    async def temp(
        self,
        interaction: discord.Interaction
    ):
        logger.info(
            "Temperature requested by %s",
            interaction.user
        )

        try:
            data = await asyncio.to_thread(
                get_sensor_data
            )

        except Exception:
            logger.exception(
                "Failed to read DHT11 sensor."
            )

            await interaction.response.send_message(
                "❌ Failed to read the sensor.",
                ephemeral=True
            )

            return

        temp = data.get("temp")
        hum = data.get("hum")

        if temp is None:
            await interaction.response.send_message(
                "⚠️ Sensor is not ready.",
                ephemeral=True
            )

            return

        if hum is None:
            humidity_text = "Unknown"
        else:
            humidity_text = f"{hum:.1f} %"

        if temp < 18:
            status = "❄️ Cold"

        elif temp < 26:
            status = "🙂 Normal"

        else:
            status = "🔥 Hot"

        embed = discord.Embed(
            title="🏠 House Sensor",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )

        embed.add_field(
            name="🌡️ Temperature",
            value=f"**{temp:.1f} °C**",
            inline=True
        )

        embed.add_field(
            name="💧 Humidity",
            value=f"**{humidity_text}**",
            inline=True
        )

        embed.add_field(
            name="📊 Status",
            value=status,
            inline=False
        )

        embed.set_footer(
            text="Raspberry Pi Temperature Sensor"
        )

        embed.set_thumbnail(
            url="https://cdn-icons-png.flaticon.com/512/728/728093.png"
        )

        await interaction.response.send_message(
            embed=embed
        )


async def setup(bot):
    await bot.add_cog(
        Sensors(bot)
    )