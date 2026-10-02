import os

import discord
from discord.ext import commands

class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel_id = int(os.getenv("WELCOME_CHANNEL_ID"))
        channel = member.guild.get_channel(channel_id)

        if channel is None:
            return

        embed = discord.Embed(
            title="👋 Welcome!",
            description=(
                f"Welcome to **{member.guild.name}**, {member.mention}!\n\n"
                "We're happy to have you here! 🎉"
            ),
            color=discord.Color.blurple()
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        embed.set_footer(
            text=f"Member #{member.guild.member_count}"
        )

        await channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Events(bot))