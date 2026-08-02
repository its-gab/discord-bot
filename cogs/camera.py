import discord
from discord.ext import commands
import cv2
import os
from datetime import datetime


class Camera(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def camera(self, ctx):

        camera = cv2.VideoCapture(0)
        #camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        #camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        if not camera.isOpened():
            await ctx.reply("❌ Webcam not found or cannot be opened")
            return

        ret, frame = camera.read()
        camera.release()

        if not ret:
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