import wifi
import github_update
import urequests
import time
import settings
import machine


def update_infuxdb(data):
    print("Sending data to influxdb...", end="")

    token = f"Bearer {settings.influxdb_token}"
    headers = {"Authorization": token}

    try:
        response = urequests.post(settings.influxdb_url, data=data, headers=headers)
    except OSError as exc:
        print(f"Error: {exc}")
        return False
    response.close()

    if response.status_code == 204:
        print("Done")
        return True
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return False


def get_rssi_level():
    return wlan.status("rssi")


if __name__ == "__main__":
    wlan = wifi.connect()
    github_update.update_firmware()

    x = 0
    error_count = 0
    while True:
        if x > 10000:
            rssi = get_rssi_level()
            data = f"Test RSSI={rssi}"

            sent_ok = update_infuxdb(data)
            if not sent_ok:
                error_count += 1
                print(f"Error count: {error_count}")
            else:
                error_count = 0
            x = 0

            if error_count >= 10:
                machine.soft_reset()

        time.sleep_ms(1)
        x += 1
