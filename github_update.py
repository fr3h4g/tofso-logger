import time
import urequests
import json
import os
import machine


def update_firmware():
    new_relase = check_new_release()

    if new_relase:
        download_release(new_relase)


def get_trees(version: str):
    headers = {"User-Agent": "tofso-logger"}
    url = f"https://api.github.com/repos/fr3h4g/tofso-logger/git/trees/{version}?recursive=1"
    response = urequests.get(url, headers=headers)
    response.close()
    # print(response.text)
    return json.loads(response.text)["tree"]


def pull_file(filename: str, tag: str):
    print(f"Downloading file {filename}...", end="")
    headers = {"User-Agent": "tofso-logger"}
    url = f"https://raw.githubusercontent.com/fr3h4g/tofso-logger/{tag}/{filename}"
    # print(url)
    response = urequests.get(url, headers=headers)
    response.close()
    # print(response.text)
    with open(filename, "w", encoding="utf8") as file:
        file.write(response.text)
    print("Done")


def check_new_release(force_new_release=False):
    print("Checking for new release on github repo fr3h4g/tofso-logger...", end="")
    headers = {"User-Agent": "tofso-logger"}
    url = "https://api.github.com/repos/fr3h4g/tofso-logger/releases"
    response = urequests.get(url, headers=headers)
    response.close()
    # print(response.text)
    if response.status_code == 200:
        releases = json.loads(response.text)
        if releases:
            latest_version = releases[0]["tag_name"]

            current_version = None
            if ".current_version" in os.listdir():
                with open(".current_version", "r", encoding="utf8") as file:
                    current_version = file.read()
            if force_new_release:
                print(f"New release found {latest_version}")
                return latest_version

            if current_version != latest_version:
                print(f"New release found {latest_version}")
                return latest_version

    print("No new release found")
    return None


def download_release(version):
    print(f"Updating firmware to release {version}...")

    trees = get_trees(version)
    for file in trees:
        # print(file)
        if file["type"] == "tree":
            try:
                os.mkdir(file["path"])
            except OSError:
                pass
        elif file["type"] == "blob":
            pull_file(file["path"], version)

    with open(".current_version", "w", encoding="utf8") as file:
        file.write(version)

    print("Update complete, resetting device in 10 seconds")
    time.sleep(10)
    machine.reset()
