import subprocess
import time
import os

from config import STATE_FILE
from utils.save import load_json


MC_CONTAINER = "minecraft"
MC_IMAGE = "itzg/minecraft-server:latest"
MC_DATA_PATH = os.getenv("MC_DATA_PATH")

mc_start_time = None

state = load_json(STATE_FILE)
mc_status_message_id = state.get("mc_status_message_id")


def docker_command(*args):
    try:
        return subprocess.run(
            ["docker", *args],
            capture_output=True,
            text=True,
            timeout=30
        )

    except subprocess.TimeoutExpired:
        return None

    except Exception as e:
        print(f"❌ Docker error: {e}")
        return None


def container_exists():
    result = docker_command(
        "inspect",
        MC_CONTAINER
    )

    return result is not None and result.returncode == 0


def container_running():
    result = docker_command(
        "inspect",
        "-f",
        "{{.State.Running}}",
        MC_CONTAINER
    )

    if result is None or result.returncode != 0:
        return False

    return result.stdout.strip() == "true"

def create_container():
    result = docker_command(
        "create",

        "--name", MC_CONTAINER,

        "--restart", "unless-stopped",

        "-p", "25565:25565",

        "-e", "VERSION=26.1.2",

        "-e", "TYPE=VANILLA",

        "-e", "MEMORY=4G",

        "-e", "MOTD=My Minecraft Server",

        "-e", "DIFFICULTY=normal",

        "-e", "MODE=survival",

        "-e", "MAX_PLAYERS=10",

        "-e", "PVP=TRUE",

        "-e", "ONLINE_MODE=TRUE",

        "-e", "EULA=TRUE",

        "-e", "ENABLE_AUTOPAUSE=TRUE",
        "-e", "AUTOPAUSE_TIMEOUT_EST=3600",
        "-e", "AUTOPAUSE_PERIOD=10",

        "-v", f"{MC_DATA_PATH}:/data",

        MC_IMAGE
    )

    if result is None:
        return "❌ Docker did not respond."

    if result.returncode != 0:
        return (
            "❌ Failed to create Minecraft container:\n"
            f"```{result.stderr.strip()}```"
        )

    return None


def start_server():
    global mc_start_time

    # Container non esistente
    if not container_exists():

        error = create_container()

        if error:
            return error

        result = docker_command(
            "start",
            MC_CONTAINER
        )

        if result is None:
            return "❌ Docker did not respond."

        if result.returncode != 0:
            return (
                "❌ Failed to start Minecraft:\n"
                f"```{result.stderr.strip()}```"
            )

        mc_start_time = time.time()

        return "🟢 Minecraft container created and started!"

    # Container già online
    if container_running():
        return "⚠️ Minecraft server is already online!"

    # Container esistente ma spento
    result = docker_command(
        "start",
        MC_CONTAINER
    )

    if result is None:
        return "❌ Docker did not respond."

    if result.returncode != 0:
        return (
            "❌ Failed to start Minecraft:\n"
            f"```{result.stderr.strip()}```"
        )

    mc_start_time = time.time()

    return "🟢 Minecraft server started!"


def stop_server():
    global mc_start_time

    if not container_exists():
        return "⚪ Minecraft container does not exist."

    if not container_running():
        return "⚠️ Minecraft server is already offline!"

    result = docker_command(
        "stop",
        MC_CONTAINER
    )

    if result is None:
        return "❌ Docker did not respond."

    if result.returncode != 0:
        return (
            "❌ Failed to stop Minecraft:\n"
            f"```{result.stderr.strip()}```"
        )

    mc_start_time = None

    return "🔴 Minecraft server stopped!"

def remove_docker():
    global mc_start_time

    if not container_exists():
        return "⚪ Minecraft container does not exist."

    result = docker_command(
        "rm",
        "-f",
        MC_CONTAINER
    )

    if result is None:
        return "❌ Docker did not respond."

    if result.returncode != 0:
        return (
            "❌ Failed to remove Minecraft container:\n"
            f"```{result.stderr.strip()}```"
        )

    mc_start_time = None

    return "🗑️ Minecraft container removed!"



def restart_server():
    global mc_start_time

    if not container_exists():
        return start_server()

    result = docker_command(
        "restart",
        MC_CONTAINER
    )

    if result is None:
        return "❌ Docker did not respond."

    if result.returncode != 0:
        return (
            "❌ Failed to restart Minecraft:\n"
            f"```{result.stderr.strip()}```"
        )

    mc_start_time = time.time()

    return "🔄 Minecraft server restarted!"


def server_status():
    if not container_exists():
        return "⚪ Minecraft server has not been created yet."

    if container_running():
        return "🟢 Minecraft server is online."

    return "🔴 Minecraft server is offline."


def accept_eula():
    return (
        "📜 Minecraft EULA is enabled.\n"
        'Docker is using `EULA=TRUE`.'
    )