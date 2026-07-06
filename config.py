import os
import discord
from discord.ext import commands
from pathlib import Path

DS_TOKEN = os.getenv("DISCORD_TOKEN")

BASE_DIR = Path(__file__).parent
STATE_FILE = BASE_DIR / "data" / "state.json"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)