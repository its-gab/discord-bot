import time
import threading

import board
import adafruit_dht  # type: ignore


sensor_data = {
    "temp": None,
    "hum": None
}

sensor_lock = threading.Lock()


def read_sensor():
    dht = None

    try:
        dht = adafruit_dht.DHT11(board.D4)

        temp = dht.temperature
        hum = dht.humidity

        if temp is not None and hum is not None:
            with sensor_lock:
                sensor_data["temp"] = temp
                sensor_data["hum"] = hum

            return True

    except Exception as e:
        print(f"[SENSOR ERROR] {e}")

    finally:
        if dht is not None:
            try:
                dht.exit()
            except Exception:
                pass

    return False


def sensor_loop():
    while True:
        read_sensor()
        time.sleep(5)


def get_sensor_data():
    with sensor_lock:
        return sensor_data.copy()


threading.Thread(
    target=sensor_loop,
    daemon=True,
    name="DHT11"
).start()