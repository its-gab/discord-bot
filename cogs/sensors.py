import asyncio

import discord
from discord import app_commands
from discord.ext import commands

from services.dht11 import get_sensor_data
from services.permissions import allowed_channel


class Sensors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="temperature",
        description="Check the Raspberry Pi temperature and humidity."
    )
    @allowed_channel("ADMIN_COMMANDS_CHANNEL_ID")
    async def temperature(self, interaction: discord.Interaction):

        await interaction.response.defer()

        data = await asyncio.to_thread(get_sensor_data)

        if data is None:
            await interaction.followup.send(
                "❌ Unable to read the DHT11 sensor."
            )
            return

        temperature = data["temperature"]
        humidity = data["humidity"]

        if temperature is None or humidity is None:
            await interaction.followup.send(
                "❌ The DHT11 sensor has no valid data."
            )
            return

        embed = discord.Embed(
            title="🌡️ Raspberry Pi Sensor",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="Temperature",
            value=f"**{temperature:.1f} °C**",
            inline=True
        )

        embed.add_field(
            name="Humidity",
            value=f"**{humidity:.1f}%**",
            inline=True
        )

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Sensors(bot))