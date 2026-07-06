import os
import time
import subprocess
import threading
import asyncio
import json
import discord
import board
import adafruit_dht
from pathlib import Path
from discord.ext import commands, tasks
from samsungtvws import SamsungTVWS
from samsungtvws.exceptions import UnauthorizedError
from mcstatus import JavaServer

DS_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

BASE_DIR = Path(__file__).parent
STATE_FILE = Path("/app/data/state.json")

mc_task = None
mc_process = None
mc_start_time = None

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


def format_uptime(seconds):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    return f"{h}h{m}m"

def load_state():
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE, "r") as f:
                return json.load(f)
    except:
        pass
    return {}

def save_state(data):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(STATE_FILE, "w") as f:
        json.dump(data, f, indent=4)


state = load_state()
mc_status_message_id = state.get("mc_status_message_id")

# Discord bot
@bot.event
async def on_ready():
    global mc_task
    print(f"Logged in as {bot.user}")

    if mc_task is None:
        mc_task = asyncio.create_task(update_mc_channel())

    if not mc_embed_loop.is_running():
        mc_embed_loop.start()

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

def create_mc_embed():
    server = JavaServer.lookup("localhost:25565")

    try:
        status = server.status()
        online = status.players.online
        max_players = status.players.max
        ping = round(status.latency)
        state = "🟢 Online"
        color = 0x00ff00
    except:
        online = 0
        max_players = 0
        ping = "N/A"
        state = "🔴 Offline"
        color = 0xff0000
    
    try:
        uptime_seconds = int(time.time() - mc_start_time)
        h = uptime_seconds // 3600
        m = (uptime_seconds % 3600) // 60
        uptime = f"{h}h {m}m"
    except:
        uptime = "N/A"
    
    embed = discord.Embed(
        title="📡 Minecraft Server Status",
        description="Live dashboard ⚡",
        color=color
    )

    embed.add_field(name="Status", value=state, inline=True)
    embed.add_field(name="Player", value=f"{online}/{max_players}", inline=True)
    embed.add_field(name="Ping", value=f"{ping} ms", inline=True)

    embed.add_field(name="Uptime", value=uptime, inline=True)
    embed.add_field(name="IP", value="localhost:25565", inline=True)
    embed.add_field(name="Update", value="every 60s", inline=True)

    embed.set_footer(text="MC Dashboard Bot 🤖")

    return embed

@tasks.loop(seconds=60)
async def mc_embed_loop():
    global mc_status_message_id

    channel_id = int(os.getenv("MC_INFO_CHANNEL_ID"))
    channel = bot.get_channel(channel_id)

    if channel is None:
        return

    embed = create_mc_embed()

    if mc_status_message_id is None:
        msg = await channel.send(embed=embed)
        mc_status_message_id = msg.id

        state = load_state()
        state["mc_status_message_id"] = mc_status_message_id
        save_state(state)
    else:
        try:
            msg = await channel.fetch_message(mc_status_message_id)
            await msg.edit(embed=embed)
        except discord.NotFound:
            msg = await channel.send(embed=embed)
            mc_status_message_id = msg.id

            state = load_state()
            state["mc_status_message_id"] = mc_status_message_id
            save_state(state)

        except discord.HTTPException as e:
            print(f"Discord error: {e}")

async def update_mc_channel():
    await bot.wait_until_ready()

    channel_id = int(os.getenv("MC_STATUS_CHANNEL_ID"))
    channel = bot.get_channel(channel_id)

    server = JavaServer.lookup("localhost:25565")

    last_state = None

    while not bot.is_closed():
        try:
            status = server.status()
            online = status.players.online
            max_players = status.players.max
            print(status.description)
            print(status.icon)
            print(status.version.name)
            print(status.latency)
            print(status.raw)

            state = f"🟢│Online"

        except Exception:
            state = "🔴│Offline"

        if state != last_state:
            last_state = state
            try:
                await channel.edit(name=state)
            except discord.HTTPException as e:
                if e.status == 429:
                    await asyncio.sleep(60)

        await asyncio.sleep(60)

@bot.command()
async def mc(ctx, action: str = None):
    global mc_process, mc_start_time

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
        
        mc_eula_file = mc_folder / "eula.txt"
        eula_file_exists = mc_eula_file.exists()

        if eula_file_exists:
            with open(mc_eula_file, "r") as f:
                content = f.read()

            if "eula=false" in content:
                await ctx.reply("❌ EULA not accepted. Please accept the EULA by using !mc eula, then start the server again.")
                return
        
        mc_process = subprocess.Popen(
            ["bash", str(mc_start_script)],
            cwd=mc_folder,
            stdin=subprocess.PIPE,
            text=True
        )

        mc_start_time = time.time()

        if eula_file_exists:
            await ctx.reply("🟢 Server started!")
        else:
            await ctx.reply("🟢 Server installed! Please accept the EULA by using !mc eula, then start the server again.")
    elif action == "eula":
        mc_eula_file = mc_folder / "eula.txt"

        if not mc_eula_file.exists():
            await ctx.reply("❌ eula.txt not found. Install the server first using !mc start.")
            return

        with open(mc_eula_file, "r") as f:
            content = f.read()

        if "eula=true" in content:
            await ctx.reply("✅ EULA already accepted.")
            return

        with open(mc_eula_file, "w") as f:
            f.write("eula=true\n")

        await ctx.reply("✅ EULA accepted! You can now start the server using !mc start.")


    elif action == "stop":
        mc_server_jar = mc_folder / "server.jar"
        
        if not mc_server_jar.exists():
            await ctx.reply("❌ server.jar not found. Download it from the official Minecraft website "
            "(https://www.minecraft.net/en-us/download/server) and place it in the 'minecraft' folder.")
            return

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
