import os
from samsungtvws import SamsungTVWS
from samsungtvws.exceptions import UnauthorizedError


def get_tv():
    return SamsungTVWS(
        host=os.getenv("TV_IP"),
        port=8002,
        token_file="token_file.txt"
    )


def get_tv_status():
    try:
        tv = get_tv()
        power = tv.rest_device_info()["device"]["PowerState"]
        return power == "on"
    except Exception:
        return None


def power_tv(action):
    try:
        status = get_tv_status()

        if status is None:
            return "❌ TV status unknown."

        tv = get_tv()

        if action == "on":
            if status:
                return "⚠️ TV already on!"
            tv.send_key("KEY_POWER")
            return "📺 TV turned on!"

        if action == "off":
            if not status:
                return "⚠️ TV already off!"
            tv.send_key("KEY_POWER")
            return "📺 TV turned off!"

        return "❌ Invalid action."

    except UnauthorizedError:
        return "❌ TV not authorized."

    except BrokenPipeError:
        return "❌ Connection interrupted."

    except Exception as e:
        return f"❌ Error: {e}"