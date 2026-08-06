import os
import cv2
import asyncio
import discord
from discord.ext import commands
from datetime import datetime
from services.camera import capture_frame


class Camera(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def camera(self, ctx):

        frame = await asyncio.to_thread(capture_frame)

        if frame is None:
            await ctx.reply("❌ Failed to capture image from webcam")
            return

        filename = f"/tmp/camera_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        cv2.imwrite(filename, frame)

        await ctx.reply(
            "📸 Photo from webcam:",
            file=discord.File(filename)
        )
        os.remove(filename)

async def setup(bot):
    await bot.add_cog(Camera(bot))