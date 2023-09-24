from urllib.parse import parse_qs, urlparse
from pathlib import Path

import re
import requests

import googleapiclient.discovery
from yt_dlp import YoutubeDL


def valid_url(url):
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
            page = requests.get(url)
            print("[YT_PLDL] URL is reachable")
            connect_success = True
            return connect_success
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
            connect_attempts += 1
            print("[YT_PLDL] cannot reach URL, retrying...")

    if not connect_success:
        print("[YT_PLDL] cannot connect to URL, check network settings")

    return connect_success


def init_API_KEY():
    secret_file = Path("secret.py")
    if secret_file.is_file():
        print("[YT_PLDL] 'secret.py' found, importing API keys...")
    else:
        print("[YT_PLDL] 'secret.py' not found, creating new...")
        API_KEY = input("[YT_PLDL] please input new API key> ")
        with open("secret.py", "w") as secret_file:
            secret_file.write(f"API_KEY = '{API_KEY}'")


init_API_KEY()
from secret import API_KEY

DEFAULT_URL = "https://www.youtube.com/playlist?list=PL8uLmtrEOEHWuyK0jfrfZ4t4QhW59JFf7"
URL = ""

# Get playlist URL, if not use default
while URL == "":
    ask_URL = input(
        "[YT_PLDL] Provide youtube playlist URL to download from (leave empty for default)> "
    )
    if ask_URL == URL:  # resort to default URL
        URL = DEFAULT_URL
    else:  # URL has been provided, check if valid
        if valid_url(ask_URL):
            URL = ask_URL


# extract playlist id from url

query = parse_qs(urlparse(URL).query, keep_blank_values=True)
playlist_id = query["list"][0]

print(f"get all playlist items links from {playlist_id}")
youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=API_KEY)

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
