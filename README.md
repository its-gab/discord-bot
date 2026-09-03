# Discord Bot

A self-hosted Discord bot written in **Python**, built with **discord.py** and **Docker**.

Designed for home-server automation, with integrations for Minecraft, Samsung Smart TV, and Raspberry Pi sensors.

## Features

* 🎮 **Minecraft** — Start, stop, restart and monitor a Minecraft server
* 📊 **Live Dashboard** — Server status, players, ping and uptime
* 📺 **Samsung TV** — Power and status control
* 🌡️ **Sensors** — Temperature and humidity monitoring via DHT11
* 🛡️ **Moderation** — Message management and member utilities
* 👋 **Welcome System** — Automatic welcome messages and roles
* 🐳 **Docker** — Fully containerized and self-hosted

## Commands

| Command             | Description            |
| ------------------- | ---------------------- |
| `!hello`            | Greeting               |
| `!ping`             | Bot latency            |
| `!clear <amount>`   | Delete messages        |
| `!mc start`         | Start Minecraft        |
| `!mc stop`          | Stop Minecraft         |
| `!mc restart`       | Restart Minecraft      |
| `!mc status`        | Minecraft status       |
| `!tv on/off/status` | Control Samsung TV     |
| `!temp`             | Temperature & humidity |

## Tech Stack

* Python 3.12+
* discord.py
* Docker & Docker Compose
* mcstatus
* Raspberry Pi / GPIO
* Samsung TV WebSocket API

## Installation

```bash
git clone https://github.com/its-gab/discord-bot.git
cd discord-bot
cp .env.example .env
```

Configure `.env`, then start the bot:

```bash
docker compose up -d --build
```

View logs:

```bash
docker compose logs -f discord-bot
```

## Project Structure

```text
discord-bot/
├── cogs/       # Discord commands
├── services/   # Integrations and core logic
├── tasks/      # Background tasks
├── utils/      # Utilities
├── main.py
├── config.py
├── Dockerfile
└── docker-compose.yml
```

## Security

Keep sensitive configuration in `.env`.

Do not commit tokens, API keys, or persistent server data.

## License

MIT License