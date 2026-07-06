# 🤖 Discord Bot

A personal, self-hosted Discord bot built with **discord.py**, designed to run on a home server (e.g. a Raspberry Pi) and integrate with a Minecraft server, a Samsung TV, and a DHT11 temperature/humidity sensor. Fully containerized with Docker.

## ✨ Features

- **General commands** — `!hello`, `!ping` (latency check)
- **Moderation** — `!clear <amount>` to bulk-delete messages
- **Welcome system** — greets new members with an embed and auto-assigns a role
- **Minecraft server management** — start/stop/restart a local Java server directly from Discord, with EULA handling
- **Live Minecraft dashboard** — an auto-updating embed showing server status, online players, ping, and uptime, refreshed every 60 seconds
- **Minecraft status channel** — renames a voice/text channel to reflect server online/offline state in real time
- **Samsung TV control** — check power status and turn the TV on/off via the local network (SmartThings/WS API)
- **House sensor readings** — `!temp` reports live temperature and humidity from a DHT11 sensor (e.g. on a Raspberry Pi GPIO pin), with a status indicator (cold/normal/hot)

## 📁 Project Structure

```
discord-bot/
├── main.py                # Entry point: loads cogs & tasks, starts the bot
├── config.py              # Bot instance, intents, env vars, paths
├── cogs/                  # Command groups
│   ├── admin.py           # Moderation commands
│   ├── events.py          # on_ready, on_member_join, etc.
│   ├── general.py         # hello, ping
│   ├── minecraft.py       # !mc start/stop/status
│   ├── sensors.py         # !temp
│   └── tv.py              # !tv on/off/status
├── tasks/                 # Background loops
│   ├── mc_embed.py        # Updates the live MC dashboard embed
│   └── mc_status.py       # Updates the MC status channel name
├── services/              # Business logic / integrations
│   ├── minecraft.py       # Process management for the MC server
│   ├── mc_embed.py        # Builds the MC status embed
│   ├── samsung_tv.py      # Samsung TV integration
│   └── dht11.py           # Reads the DHT11 sensor in a background thread
├── utils/
│   ├── formatter.py       # Uptime formatting helper
│   └── save.py            # JSON state persistence
├── minecraft/
│   └── start.sh           # Launch script for the MC server (server.jar not included)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## ⚙️ Requirements

- Python 3.12+ (or Docker)
- A Discord bot token ([Discord Developer Portal](https://discord.com/developers/applications))
- *(Optional)* A Minecraft Java server (`server.jar`, downloaded separately) if you want Minecraft features
- *(Optional)* A Samsung TV on the same network for TV control
- *(Optional)* A DHT11 sensor wired to a Raspberry Pi GPIO pin for sensor readings

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| `DISCORD_TOKEN` | Your Discord bot token |
| `WELCOME_CHANNEL_ID` | Channel ID where welcome messages are sent |
| `NEW_MEMBER_ROLE_ID` | Role ID automatically assigned to new members |
| `MC_STATUS_CHANNEL_ID` | Channel ID renamed to show Minecraft online/offline status |
| `MC_INFO_CHANNEL_ID` | Channel ID where the live Minecraft dashboard embed is posted |
| `TV_IP` | Local IP address of your Samsung TV |

## 🚀 Getting Started

### Option 1 — Docker (recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/its-gab/discord-bot.git
   cd discord-bot
   ```
2. Edit the environment variables in `docker-compose.yml` (or use a `.env` file) with your real values.
3. *(Optional)* If you want Minecraft support, place `server.jar` and an accepted `eula.txt` inside the `minecraft/` folder.
4. Build and run:
   ```bash
   docker compose up -d --build
   ```

### Option 2 — Local (Python)

1. Clone the repository and install dependencies:
   ```bash
   git clone https://github.com/its-gab/discord-bot.git
   cd discord-bot
   pip install -r requirements.txt
   ```
2. Export the required environment variables (see table above).
3. Run the bot:
   ```bash
   python main.py
   ```

> ⚠️ Note: `adafruit-blinka`, `adafruit-circuitpython-dht`, and `lgpio` require GPIO hardware access and are intended to run on a Raspberry Pi. Running elsewhere may cause the sensor cog to fail on startup.

## 📜 Commands

| Command | Description |
|---|---|
| `!hello` | Bot replies with a greeting |
| `!ping` | Shows bot latency |
| `!clear [amount]` | Deletes the last `amount` messages (default: 5) |
| `!mc start` \| `stop` \| `status` | Manage the Minecraft server |
| `!tv on` \| `off` \| `status` | Control the Samsung TV |
| `!temp` | Shows current temperature & humidity |

## 🐳 Docker Notes

- The container installs a JDK (`openjdk-25-jre`) to be able to run the Minecraft server as a subprocess.
- `privileged: true` and volume mounts are used so the container can access GPIO hardware and persist Minecraft world data / bot state.
- Port `25565` is exposed for the Minecraft server.

## 📄 License

This project is licensed under the [MIT License](LICENSE).
