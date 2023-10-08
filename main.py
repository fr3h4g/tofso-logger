import wifi
import github_update
import urequests
import time
import settings


def update_infuxdb(data):
    print("Sending data to influxdb...", end="")

    token = f"Bearer {settings.influxdb_token}"
    headers = {"Authorization": token}

    response = urequests.post(settings.influxdb_url, data=data, headers=headers)
    response.close()
    if response.status_code == 204:
        print("Done")
    else:
        print(f"Error: {response.status_code} - {response.text}")


if __name__ == "__main__":
    wlan = wifi.connect()
    github_update.update_firmware()

    while True:
        rssi = wlan.status("rssi")
        data = f"Test RSSI={rssi}"

        update_infuxdb(data)

        time.sleep(10)
