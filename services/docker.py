import subprocess
import logging

def docker_command(*args):
    try:
        result = subprocess.run(
            ["docker", *args],
            capture_output=True,
            text=True,
            timeout=30
        )

        return result

    except subprocess.TimeoutExpired:
        return None

    except Exception as e:
        logging.error(f"Docker: {e}")
        return None

def container_exists(name: str) -> bool:
    result = docker_command(
        "inspect",
        name
    )

    return result is not None and result.returncode == 0

def container_running(name: str) -> bool:
    result = docker_command(
        "inspect",
        "-f",
        "{{.State.Running}}",
        name
    )

    if result is None or result.returncode != 0:
        return False

    return result.stdout.strip() == "true"

def create_container(name: str, image: str, *args):
    return docker_command(
        "create",
        "--name",
        name,
        *args,
        image
    )

def start_container(name: str):
    return docker_command(
        "start",
        name
    )

def stop_container(name: str):
    return docker_command(
        "stop",
        name
    )

def restart_container(name: str):
    return docker_command(
        "restart",
        name
    )

def remove_container(name: str):
    return docker_command(
        "rm",
        "-f",
        name
    )