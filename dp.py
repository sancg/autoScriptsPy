#!/usr/bin/env python3
import json
import time
import argparse
import subprocess
import signal
from pathlib import Path

# Constants -----------------------------
ROOT_DIR = Path(__file__).parent.resolve()    # constant root
DEFAULT_JSON_DIR = ROOT_DIR / "playlists"     # store JSON files here

COOKIES = ROOT_DIR / "cookies.txt"

# Defaults (you can tune)
MIN_DELAY = 1
MAX_DELAY = 20
INITIAL_DELAY = 2
# ----------------------------------------

interrupt_flag = False


def signal_handler(sig, frame):
    global interrupt_flag
    interrupt_flag = True
    print("\n[DOWNLOADER] Interrupt detected... preparing safe shutdown.")


signal.signal(signal.SIGINT, signal_handler)


def load_json(path):
    with open(path, "r", encoding="utf8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf8") as f:
        json.dump(data, f, indent=2)


def download_video(url):
    # Blocking call—waits until yt-dlp finishes
    try:
        subprocess.run(["yt-dlp", url], check=True)
        return True
    except Exception as e:
        print(f'[DOWNLOADER] An exception occurred: {e}')
        return False


def run(json_file):
    data = load_json(json_file)
    playlist = data.get('playlist') or data.get('playList')
    print(playlist)

    original_size = len(playlist)
    processed = 0
    while playlist:
        if interrupt_flag:
            print("[DOWNLOADER] Shutting down successful")
            break

        processed += 1
        item = playlist[0]
        print(
            f"[DOWNLOADER] {processed} / {original_size}: {item['title']}")

        ok = download_video(item["url"])

        # Remove this item
        if not ok:
            break
        else:
            print("[DOWNLOADER] Removing entry from File...")
            data["playList"].pop(0)
            save_json(json_file, data)

        time.sleep(1)
        print("---------------------------------------------")
    print("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", required=True, help="JSON playlist file")
    args = parser.parse_args()

    json_path = Path(args.f)
    if not json_path.exists():
        json_path = DEFAULT_JSON_DIR / args.f

    run(json_path)
