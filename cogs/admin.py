import discord
from discord import app_commands
from discord.ext import commands

from services.permissions import owner_only


class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @owner_only()
    @app_commands.command(
        name="clear",
        description="Delete messages from the current channel."
    )
    @app_commands.describe(
        amount="Number of messages to delete (default: 5)."
    )
    async def clear(self, interaction: discord.Interaction, amount: int = 5):
        if amount < 1:
            await interaction.response.send_message(
                "❌ Amount must be at least 1.",
                ephemeral=True
            )
            return

        if amount > 100:
            await interaction.response.send_message(
                "❌ You can delete a maximum of 100 messages at once.",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        deleted = await interaction.channel.purge(limit=amount)

        await interaction.followup.send(
            f"🗑️ Deleted {len(deleted)} messages.",
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Admin(bot))