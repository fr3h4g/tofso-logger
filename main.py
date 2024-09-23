import wifi
import github_update
import urequests
import time
import settings
import machine
import dht
import random
from machine import WDT

count_meter_1 = 0
count_meter_2 = 0
error_count = 0
wdt = None


def update_infuxdb(data):
    print("Sending data to influxdb...", end="")

    token = f"Bearer {settings.influxdb_token}"
    headers = {"Authorization": token}

    try:
        response = urequests.post(settings.influxdb_url, data=data, headers=headers)
        response.close()
    except Exception as exc:
        print(f"Error: {exc}")
        return False

    if response.status_code == 204:
        print("Done")
        return True
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return False


def get_rssi_level(wlan):
    rssi = wlan.status("rssi")
    return rssi


def get_temp_humid(sensor):
    sensor.measure()
    temperature = sensor.temperature()
    humidity = sensor.humidity()
    return temperature, humidity


def TriggerCountMeter1(Source):
    global count_meter_1
    count_meter_1 += 1


def TriggerCountMeter2(Source):
    global count_meter_2
    count_meter_2 += 1


def send_data(Source):
    global count_meter_1, count_meter_2, error_count, led, sensor, wlan, wtd
    led.value(1)

    # temp, humid = get_temp_humid(sensor)
    temp = 0
    humid = 0
    rssi = get_rssi_level(wlan)

    data = f"Test RSSI={rssi}\nTest Temperature={temp}\nTest Humidity={humid}\nTest Meter_1={count_meter_1}\nTest Meter_2={count_meter_2}"
    count_meter_1 = 0
    count_meter_2 = 0

    sent_ok = update_infuxdb(data)
    if not sent_ok:
        error_count += 1
        print(f"Error count: {error_count}")
    else:
        error_count = 0

    if error_count >= 5:
        print("Error sending data to InfluxDB, reseting device")
        machine.reset()
    
    wdt.feed()

    led.value(0)

def feed_watchdog(Source):
    global wdt
    wdt.feed()
    print("wdt_feed")

def update(Source):
    led.value(1)
    if github_update.check_new_release():
        time.sleep(10)
        machine.reset()
    led.value(0)


if __name__ == "__main__":
    wdt = WDT(timeout=5_000)
    tim_wdt = machine.Timer(period=1000, mode=machine.Timer.PERIODIC, callback=feed_watchdog)

    led = machine.Pin("LED", machine.Pin.OUT)
    pwm0 = machine.PWM(machine.Pin(0), freq=100, duty_u16=1000)

    led.value(1)

    triggerPinMeter1 = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP)
    triggerPinMeter2 = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP)

    sensor = dht.DHT11(machine.Pin(2))

    wlan = wifi.connect()
    github_update.update_firmware()
    
    error_count = 0

    triggerPinMeter1.irq(
        trigger=machine.Pin.IRQ_FALLING, handler=TriggerCountMeter1, hard=True
    )
    triggerPinMeter2.irq(
        trigger=machine.Pin.IRQ_FALLING, handler=TriggerCountMeter2, hard=True
    )

    tim = machine.Timer(period=10_000, mode=machine.Timer.PERIODIC, callback=send_data)

    tim2 = machine.Timer(period=300_000, mode=machine.Timer.PERIODIC, callback=update)

    tim_wdt.deinit()

    while True:
        try:
            wdt.feed()
            led.value(1)
            time.sleep_ms(50)
            led.value(0)
            time.sleep_ms(1000)

        except KeyboardInterrupt:
            tim.deinit()
            tim2.deinit()
            machine.soft_reset()

