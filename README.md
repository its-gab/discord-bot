# Discord Bot

A Python-based Discord bot for community management, GitHub release monitoring, Steam wishlist tracking, Minecraft server administration, and Raspberry Pi system monitoring.

The bot dynamically loads cogs from the `cogs/` directory, stores persistent JSON state under `data/`, and uses environment-based channel permissions to restrict commands by location and owner.

## Features

- General bot commands
  - `/ping`
  - `/about`
  - `/uptime`
  - `/stats`
- Welcome message automation on member join
- Admin utilities
  - `/clear`
- GitHub repository monitoring
  - `/github add <url>`
  - `/github remove <url>`
  - `/github list`
  - Sends Discord notifications when a monitored repository publishes a new release
- Steam wishlist discount tracking
  - Periodically checks a Steam wishlist for discounted games
  - Updates a channel embed with current deals
- Minecraft server management
  - `/minecraft start`
  - `/minecraft stop`
  - `/minecraft restart`
  - `/minecraft status`
  - `/minecraft remove`
  - Creates and manages a Dockerized Minecraft server instance
- Raspberry Pi / host monitoring
  - `/server uptime`
  - `/server info`
  - `/server docker`
  - `/temperature`
  - Reads system uptime, CPU, memory, disk, local IP, Docker container list, and DHT11 sensor data

## Tech stack

- Python 3.13
- discord.py
- requests
- psutil
- mcstatus
- Docker

## Project structure

```text
.
├── cogs/                  # Discord command groups and background tasks
│   ├── admin.py
│   ├── events.py
│   ├── general.py
│   ├── github.py
│   ├── minecraft.py
│   ├── sensors.py
│   ├── server.py
│   └── steam.py
├── services/              # API calls, Docker helpers, and monitoring logic
│   ├── dht11.py
│   ├── discounts_embed.py
│   ├── docker.py
│   ├── github.py
│   ├── mc_embed.py
│   ├── minecraft.py
│   ├── permissions.py
│   ├── server.py
│   ├── steam.py
│   └── utils.py
├── data/                  # Persistent JSON state files generated at runtime
├── .env.example           # Example environment configuration
├── .gitignore
├── config.py              # Shared paths for state files
├── docker-compose.yml     # Runtime configuration for the bot container
├── Dockerfile
├── LICENSE
├── main.py                # Entry point; loads all cogs
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.13+
- A Discord bot token
- A Discord server with configured channels
- Docker installed if you want to manage the Minecraft server container
- Optional: a Raspberry Pi or host machine running the monitoring tools

## Configuration

Copy `.env.example` to `.env` and populate it with your values:

```env
DISCORD_TOKEN=your_discord_bot_token
OWNER_ID=your_discord_user_id
STEAM_ID=your_steam_profile_id
SENSOR_API_URL=http://host.docker.internal:8765/sensor

ADMIN_COMMANDS_CHANNEL_ID=channel_id
COMMANDS_CHANNEL_ID=channel_id
WELCOME_CHANNEL_ID=channel_id
MINECRAFT_INFO_CHANNEL_ID=channel_id
MINECRAFT_COMMANDS_CHANNEL_ID=channel_id
STEAM_WISHLIST_CHANNEL_ID=channel_id
GITHUB_UPDATES_CHANNEL_ID=channel_id

MC_DATA_PATH=/path/to/minecraft/data
```

### Environment behavior

- `DISCORD_TOKEN` is required to authenticate the bot
- `OWNER_ID` restricts sensitive admin and server commands to the bot owner
- Channel IDs are used by `services/permissions.py` to control where certain commands are allowed
- `MC_DATA_PATH` is required for Docker-based Minecraft server management
- `SENSOR_API_URL` is used for DHT11 sensor reads

## Installation

### Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env with your bot settings
python main.py
```

### Docker

```bash
docker compose up --build -d
```

The included Docker setup mounts the local `data/` directory and exposes the Docker socket so the bot can manage containers on the host.

## Command permissions

The bot uses two protection layers:

- `allowed_channel(...)`: restricts commands to specific Discord channels based on environment variables
- `owner_only()`: restricts sensitive commands to the configured `OWNER_ID`

This is especially important for admin, Minecraft, and server-management commands.

## Runtime behavior

- On startup, `main.py` loads each Python file in `cogs/` as a Discord cog
- Background loops monitor:
  - GitHub repository releases every 6 hours
  - Steam wishlist discounts every 6 hours
  - Minecraft status/embed updates every 60 seconds
- Bot state such as tracked repositories and embed message IDs is saved to JSON files under `data/`

## Notes

- The bot is designed for a self-hosted setup and expects direct access to Docker and host system resources.
- Some features are intended for a Raspberry Pi or another Linux-like host, particularly the server statistics and sensor commands.
- The bot can be extended by adding more cogs under `cogs/` without changing the main boot process.

## License

This project is distributed under the MIT License. See [LICENSE](LICENSE) for details.
