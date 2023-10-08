import time
import wifi
import urequests

wifi.connect()

headers = {"User-Agent": "tofso-logger"}
url = "https://api.github.com/repos/fr3h4g/tofso-logger/releases"
response = urequests.get(url, headers=headers)
print(response.text)
