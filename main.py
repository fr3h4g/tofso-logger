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
    except Exception as exc:
        print(f"Error: {exc}")
        return False
    response.close()

    if response.status_code == 204:
        print("Done")
        return True
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return False


def get_rssi_level(wlan):
    return wlan.status("rssi")


if __name__ == "__main__":
    wlan = wifi.connect()
    github_update.update_firmware()

    send_influxdb_data_wait = 0
    check_for_firmware_update_wait = 0
    error_count = 0
    while True:
        if send_influxdb_data_wait > 10_000:
            rssi = get_rssi_level(wlan)
            data = f"Test RSSI={rssi}"

            sent_ok = update_infuxdb(data)
            if not sent_ok:
                error_count += 1
                print(f"Error count: {error_count}")
            else:
                error_count = 0
            send_influxdb_data_wait = 0

            if error_count >= 5:
                print("Error sending data to InfluxDB, reseting device")
                machine.reset()

        if check_for_firmware_update_wait > 100_000:
            if github_update.check_new_release():
                time.sleep(10)
                machine.reset()
            check_for_firmware_update_wait = 0

        time.sleep_ms(1)
        send_influxdb_data_wait += 1
        check_for_firmware_update_wait += 1
