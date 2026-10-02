import os

from services.docker import (
    container_exists,
    container_running,
    create_container,
    start_container,
    stop_container,
    restart_container,
    remove_container,
)


MC_CONTAINER = "minecraft"
MC_IMAGE = "itzg/minecraft-server:latest"
MC_DATA_PATH = os.getenv("MC_DATA_PATH")


def _docker_error(result, action: str):
    if result is None:
        return f"Docker did not respond while trying to {action}."

    if result.returncode != 0:
        error = result.stderr.strip()

        if error:
            return f"Failed to {action}: {error}"

        return f"Failed to {action}."

    return None


def create_minecraft_container():
    if not MC_DATA_PATH:
        return False, "MC_DATA_PATH is not configured."

    if container_exists(MC_CONTAINER):
        return True, None

    result = create_container(
        MC_CONTAINER,
        MC_IMAGE,

        "--restart", "no",

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
    )

    error = _docker_error(result, "create the Minecraft container")

    if error:
        return False, error

    return True, None


def start_server():
    if not container_exists(MC_CONTAINER):
        success, error = create_minecraft_container()

        if not success:
            return False, error

    if container_running(MC_CONTAINER):
        return False, "Minecraft server is already online."

    result = start_container(MC_CONTAINER)

    error = _docker_error(result, "start Minecraft")

    if error:
        return False, error

    return True, None


def stop_server():
    if not container_exists(MC_CONTAINER):
        return False, "Minecraft container does not exist."

    if not container_running(MC_CONTAINER):
        return False, "Minecraft server is already offline."

    result = stop_container(MC_CONTAINER)

    error = _docker_error(result, "stop Minecraft")

    if error:
        return False, error

    return True, None


def restart_server():
    if not container_exists(MC_CONTAINER):
        return False, "Minecraft container does not exist."

    result = restart_container(MC_CONTAINER)

    error = _docker_error(result, "restart Minecraft")

    if error:
        return False, error

    return True, None


def remove_server():
    if not container_exists(MC_CONTAINER):
        return False, "Minecraft container does not exist."

    result = remove_container(MC_CONTAINER)

    error = _docker_error(result, "remove the Minecraft container")

    if error:
        return False, error

    return True, None


def server_status():
    if not container_exists(MC_CONTAINER):
        return "not_created"

    if container_running(MC_CONTAINER):
        return "online"

    return "offline"