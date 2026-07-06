import os
import time
import subprocess
import threading
import socket
import discord
import board
import adafruit_dht
from pathlib import Path
from discord.ext import commands
from samsungtvws import SamsungTVWS
from samsungtvws.exceptions import UnauthorizedError

DS_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

BASE_DIR = Path(__file__).parent

mc_process = None

# initialize sensors
dht = adafruit_dht.DHT11(board.D4)

sensor_data = {
    "temp": None,
    "hum": None
}

# Sensor loop (thread)
def sensor_loop():
    global sensor_data

    while True:
        try:
            temp = dht.temperature
            hum = dht.humidity

            if temp is not None and hum is not None:
                sensor_data["temp"] = temp
                sensor_data["hum"] = hum

                print(f"[SENSOR] {temp}°C {hum}%")

        except Exception as e:
            print("[SENSOR ERROR]", e)

        time.sleep(5)


# Start sensor thread
threading.Thread(target=sensor_loop, daemon=True).start()


# Discord bot
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_member_join(member):
    channel_id = int(os.getenv("WELCOME_CHANNEL_ID"))
    channel = bot.get_channel(channel_id)

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
    role_id = os.getenv("NEW_MEMBER_ROLE_ID")

    if role_id:
        role = member.guild.get_role(int(role_id))
        if role:
            await member.add_roles(role)


@bot.command()
async def hello(ctx):
    await ctx.reply(f"Hello {ctx.author.mention}!👋",)

@bot.command()
async def clear(ctx, amount: int = 5):
    await ctx.message.delete()
    await ctx.channel.purge(limit=amount + 1)

@bot.command()
async def ping(ctx):
    message = await ctx.send("🏓 Ping...")
    latency = round(bot.latency * 1000)
    await message.edit(content=f"🏓 Pong! {latency}ms")


@bot.command()
async def temp(ctx):
    temp = sensor_data["temp"]
    hum = sensor_data["hum"]

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

    # 🔥 stato qualità
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




@bot.command()
async def tv(ctx, action: str):
    try:
        samsungtv = SamsungTVWS(
            host=os.getenv("TV_IP"),
            port=8002,
            token_file="token_file.txt"
        )

        action = action.lower()
        status = samsungtv.rest_device_info()["device"]["PowerState"]

        if not status:
            await ctx.reply("❌ TV not connected.")
            return
        
        if status != "on":
            status = "off"

        if action == "status":
            await ctx.reply("📺 TV is " + status + "!")
            return
            
        if action == status:
            await ctx.reply("⚠️ TV already " + status + "!")

        elif action == "off" or action == "on":
            samsungtv.send_key("KEY_POWER")
            await ctx.reply("📺 TV " + action + "!")

        else:
            await ctx.reply("❌ Use: !tv on - !tv off")
            return
    except UnauthorizedError:
        await ctx.reply("❌ TV not authorized.")
    except BrokenPipeError:
        await ctx.reply("❌ Connection with the TV interrupted.")
    except Exception as e:
        print(e)
        await ctx.reply(f"❌ Error: {e}")

@bot.command()
async def mc(ctx, action: str = None):
    global mc_process

    if action is None:
        await ctx.reply("❌ No argument provided. Use: !mc start - !mc stop - !mc status")
        return
    
    action = action.lower()

    mc_folder = BASE_DIR / "minecraft"

    if action == "start":
        if mc_process and mc_process.poll() is None:
            await ctx.reply("⚠️ Server is already online!")
            return

        mc_server_jar = mc_folder / "server.jar"
        mc_start_script = mc_folder / "start.sh"

        if not mc_server_jar.exists():
            await ctx.reply("❌ server.jar not found. Download it from the official Minecraft website "
            "(https://www.minecraft.net/en-us/download/server) and place it in the 'minecraft' folder.")
            return

        if not mc_start_script.exists():
            await ctx.reply("❌ start.sh not found.")
            return
    
        mc_process = subprocess.Popen(
            ["bash", str(mc_start_script)],
            cwd=mc_folder,
            stdin=subprocess.PIPE,
            text=True
        )
        await ctx.reply("🟢 Server started!")


    elif action == "stop":
        if mc_process is None or mc_process.poll() is not None:
            await ctx.reply("⚠️ Server is already offline!")
            return

        try:
            mc_process.stdin.write("stop\n")
            mc_process.stdin.flush()
        except Exception:
            mc_process.terminate()

        mc_process = None
        await ctx.reply("🔴 Server stopped!")


    elif action == "status":
        if mc_process and mc_process.poll() is None:
            await ctx.reply("🟢 Server is online")
        else:
            await ctx.reply("🔴 Server is offline")

bot.run(DS_TOKEN)
