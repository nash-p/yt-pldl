import googleapiclient.discovery
from urllib.parse import parse_qs, urlparse
from secret import API_KEY

# extract playlist id from url
url = "https://www.youtube.com/playlist?list=PL8uLmtrEOEHWuyK0jfrfZ4t4QhW59JFf7"
query = parse_qs(urlparse(url).query, keep_blank_values=True)
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
playlist_url_List = [
    f'https://www.youtube.com/watch?v={t["snippet"]["resourceId"]["videoId"]}'
    for t in playlist_items
]
print(playlist_url_List)
