from urllib.parse import parse_qs, urlparse
from pathlib import Path

import sys
import re
import requests

import googleapiclient.discovery
from yt_dlp import YoutubeDL


def valid_api_key(key):
    '''returns True if API key is valid'''
    req = requests.get(
        f'https://www.googleapis.com/youtube/v3/search?part=snippet&q=YouTube+Data+API&type=video&key={key}',
        timeout=5
    )
    if req.status_code == 200:
        print("[YT_PLDL] API key is valid")
        return True

    print("[YT_PLDL] API key is not valid")
    return False


def init_api_key():
    '''creates a file 'secret.py containing user provided API key'''
    secret_file = Path("secret.py")

    is_valid = False
    attempt_key = 0
    while not is_valid and attempt_key < 3:
        new_key = input("[YT_PLDL] please input new API key> ")
        is_valid = valid_api_key(new_key)
        attempt_key += 1

    if not is_valid:
        print("[YT_PLDL] Too many attempts [3]. Exiting")
        sys.exit()

    with open(file="./secret.py", mode="a", encoding="utf-8") as secret_file:
        secret_file.write(f"API_KEY='{new_key}'")
        secret_file.flush()
        secret_file.close()


def valid_url(url):
    '''returns Trues if the playlist url matches regex and is reachable'''
    pattern = re.compile(
        r"(https?://)?(www\.)?youtube\.com/playlist\?list=[\w-]+",
        re.IGNORECASE,
    )

    valid_pattern = pattern.match(url) is not None

    if not valid_pattern:
        print("[YT_PLDL] Please provide a valid URL")
        return False

    print("[YT_PLDL] URL is valid")

    connect_attempts = 0
    connect_success = False
    while connect_attempts < 3 and not connect_success:
        try:
            requests.get(url, timeout=10)
            print("[YT_PLDL] URL is reachable")
            connect_success = True
            return connect_success
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
            connect_attempts += 1
            print("[YT_PLDL] cannot reach URL, retrying...")

    if not connect_success:
        print("[YT_PLDL] cannot connect to URL, check network settings")

    return connect_success


def main():
    '''entry point'''

    try:
        from secret import API_KEY
    except ImportError:
        print("[YT_PLDL] 'secret.py' not found, creating new...")
        init_api_key()
        from secret import API_KEY

    if not valid_api_key(API_KEY):
        init_api_key()

    default_url = "https://www.youtube.com/playlist?list=PL8uLmtrEOEHWuyK0jfrfZ4t4QhW59JFf7"
    URL = ""

    # Get playlist URL, if not use default
    while URL == "":
        ask_URL = input(
            "[YT_PLDL] Provide youtube playlist URL to download from (leave empty for default)> "
        )
        if ask_URL == URL:  # resort to default URL
            URL = default_url
        else:  # URL has been provided, check if valid
            if valid_url(ask_URL):
                URL = ask_URL

    # extract playlist id from url

    query = parse_qs(urlparse(URL).query, keep_blank_values=True)
    playlist_id = query["list"][0]

    print(f"get all playlist items links from {playlist_id}")
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", developerKey=API_KEY)

    request = youtube.playlistItems().list(
        part="snippet", playlistId=playlist_id, maxResults=50
    )
    response = request.execute()

    playlist_items = []
    while request is not None:
        response = request.execute()
        playlist_items += response["items"]
        request = youtube.playlistItems().list_next(request, response)

    print(f"total: {len(playlist_items)}")
    playlist_urls = [
        f'https://www.youtube.com/watch?v={t["snippet"]["resourceId"]["videoId"]}'
        for t in playlist_items
    ]
    print(playlist_urls)

    ydl_opts = {
        "format": "18",
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download(playlist_urls)


if __name__ == '__main__':
    main()
