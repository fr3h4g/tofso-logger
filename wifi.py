import network
import time
from settings import ssid, password
import machine


def connect():
    wlan = None
    try:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(ssid, password)
    except Exception as exc:
        print(f"Error: {exc}")
        print("Error connecting to wifi, reseting device in 10 seconds")
        time.sleep(10)
        machine.reset()

    if wlan:
        # Wait for connect or fail
        max_wait = 30
        while max_wait > 0:
            if wlan.status() < 0 or wlan.status() >= 3:
                break
            max_wait -= 1
            print("Waiting for connection...")
            time.sleep(1)

        # Handle connection error
        if wlan.status() != 3:
            print("Error connecting to wifi, reseting device in 10 seconds")
            time.sleep(10)
            machine.reset()

        print(f"Connected to wifi '{ssid}'")
        return wlan
