import time
import threading

import board
import adafruit_dht # type: ignore

sensor_data = {
    "temp": None,
    "hum": None
}

# initialize sensor
dht = adafruit_dht.DHT11(board.D4)

def sensor_loop():
    global sensor_data

    while True:
        try:
            temp = dht.temperature
            hum = dht.humidity

            if temp is not None and hum is not None:
                sensor_data["temp"] = temp
                sensor_data["hum"] = hum

        except Exception as e:
            print("[SENSOR ERROR]", e)

        time.sleep(5)

def get_sensor_data():
    return sensor_data

# Start sensor thread
threading.Thread(target=sensor_loop, daemon=True).start()