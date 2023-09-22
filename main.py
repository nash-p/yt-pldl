from urllib.parse import parse_qs, urlparse

import re

import googleapiclient.discovery
from yt_dlp import YoutubeDL

from secret import API_KEY


def valid_url(url):
    pattern = re.compile(
        r"(https?://)?(www\.)?youtube\.com/playlist\?list=[\w-]+",
        re.IGNORECASE,
    )

    valid_pattern = pattern.match(ask_URL) is not None
    if not valid_pattern:
        print("[YT_PLDL] Please provide a valid URL")
        return False

    return True


DEFAULT_URL = "https://www.youtube.com/playlist?list=PL8uLmtrEOEHWuyK0jfrfZ4t4QhW59JFf7"
URL = ""

# Get playlist URL, if not use default
while URL == "":
    ask_URL = input(
        "[YT_PLDL] Provide youtube playlist URL to download from (leave empty for default)>"
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
