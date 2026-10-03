import socket
import subprocess
import psutil


def get_cpu_usage():
    return psutil.cpu_percent()


def get_ram():
    ram = psutil.virtual_memory()

    return {
        "used": ram.used,
        "total": ram.total,
        "percent": ram.percent
    }


def get_disk():
    disk = psutil.disk_usage("/")

    return {
        "used": disk.used,
        "total": disk.total,
        "percent": disk.percent
    }


def get_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return int(f.read()) / 1000
    except Exception as e:
        print(f"Error: {e}")
        return None


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()

        return ip

    except Exception as e:
        print(f"Error: {e}")
        return None


def get_system_uptime():
    with open("/proc/uptime") as f:
        return int(float(f.readline().split()[0]))

def docker_containers():
    try:
        output = subprocess.check_output(
            ["docker", "ps", "--format", "{{.Names}}|{{.Status}}"]
        ).decode().strip()

        if not output:
            return []

        containers = []

        for line in output.splitlines():
            name, status = line.split("|")
            containers.append((name, status))

        return containers

    except Exception as e:
        print(f"Error: {e}")
        return None