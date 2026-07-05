import os, time, discord, board # type: ignore
import adafruit_dht # type: ignore
from discord.ext import commands # type: ignore

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f"Connesso come {bot.user}")

@bot.command()
async def ciao(ctx):
    await ctx.send(f"Ciao {ctx.author.mention}! 👋")

@bot.command()
async def say(ctx, *, msg):
    await ctx.send(msg)


dht = adafruit_dht.DHT11(board.D4)

last_temp = None
last_hum = None
last_time = 0

@bot.command()
async def temp(ctx):
    global last_temp, last_hum, last_time

    if time.time() - last_time < 5 and last_temp is not None:
        await ctx.send(
            f"🌡️ {last_temp:.1f} °C\n"
            f"💧 {last_hum:.0f}% (cached)"
        )
        return

    try:
        last_temp = dht.temperature
        last_hum = dht.humidity
        last_time = time.time()

        await ctx.send(
            f"🌡️ {last_temp:.1f} °C\n"
            f"💧 {last_hum:.0f}%"
        )
    except RuntimeError as E:
        await ctx.send(str(E))
    

bot.run(TOKEN)