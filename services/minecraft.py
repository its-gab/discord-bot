import time
import subprocess

from config import BASE_DIR, STATE_FILE
from utils.save import load_json

mc_folder = BASE_DIR / "minecraft"

mc_process = None
mc_start_time = None

state = load_json(STATE_FILE)
mc_status_message_id = state.get("mc_status_message_id")


def start_server():
    global mc_process, mc_start_time

    if mc_process and mc_process.poll() is None:
        return "⚠️ Server is already online!"

    mc_server_jar = mc_folder / "server.jar"
    mc_start_script = mc_folder / "start.sh"

    if not mc_server_jar.exists():
        return "❌ server.jar not found"

    if not mc_start_script.exists():
        return "❌ start.sh not found"

    mc_eula_file = mc_folder / "eula.txt"

    if mc_eula_file.exists():
        content = mc_eula_file.read_text()
        if "eula=false" in content:
            return "❌ EULA not accepted"

    mc_process = subprocess.Popen(
        ["bash", str(mc_start_script)],
        cwd=mc_folder,
        stdin=subprocess.PIPE,
        text=True
    )

    mc_start_time = time.time()

    return "🟢 Server started!"


def stop_server():
    global mc_process, mc_start_time

    mc_server_jar = mc_folder / "server.jar"

    if not mc_server_jar.exists():
        return "❌ server.jar not found"

    if mc_process is None or mc_process.poll() is not None:
        return "⚠️ Server is already offline!"

    try:
        if mc_process.stdin:
            mc_process.stdin.write("stop\n")
            mc_process.stdin.flush()
        else:
            mc_process.terminate()
    except Exception:
        mc_process.terminate()

    mc_process = None
    mc_start_time = None

    return "🔴 Server stopped!"

def server_status():
    if mc_process and mc_process.poll() is None:
        return "🟢 Server is online"
    else:
        return "🔴 Server is offline"


def restart_server():
    stop_server()
    time.sleep(2)
    return start_server()


def accept_eula():
    mc_eula_file = mc_folder / "eula.txt"

    if not mc_eula_file.exists():
        return "❌ eula.txt not found"

    content = mc_eula_file.read_text()

    if "eula=true" in content:
        return "✅ EULA already accepted"

    mc_eula_file.write_text("eula=true\n")

    return "✅ EULA accepted!"