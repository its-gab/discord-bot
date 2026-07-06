import os

import discord
from discord.ext import commands


class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as {self.bot.user}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel_id = int(os.getenv("WELCOME_CHANNEL_ID"))
        role_id = int(os.getenv("NEW_MEMBER_ROLE_ID"))

        channel = self.bot.get_channel(channel_id)

        # Send a welcome message in the welcome channel
        if channel:
            embed = discord.Embed(
                title="🎉 Welcome!",
                description=f"Hello {member.mention}, welcome to the server! 😄",
                color=0x00ffcc
            )

            embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
            embed.set_footer(text=f"User #{member.guild.member_count}")

            await channel.send(embed=embed)

        # Give the new member a role
        if role_id:
            role = member.guild.get_role(role_id)
            if role:
                await member.add_roles(role)


async def setup(bot):
    await bot.add_cog(Events(bot))