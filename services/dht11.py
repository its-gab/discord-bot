import os
import requests

SENSOR_API_URL = os.getenv("SENSOR_API_URL")


def get_sensor_data():
    try:
        response = requests.get(
            SENSOR_API_URL,
            timeout=2
        )
        response.raise_for_status()

        data = response.json()

        return {
            "temperature": data.get("temperature"),
            "humidity": data.get("humidity"),
        }

    except (requests.RequestException, ValueError):
        return None