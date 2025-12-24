from googleapiclient.discovery import build
import pandas as pd
from datetime import datetime

api_key = "AIzaSyAVCxOYVwFPP8EruwXP9FY4K8oqgqGPCJA"
youtube = build("youtube", "v3", developerKey=api_key)

# List of countries you want to get trending data for
countries = ["US", "FR", "GB"]  # You can add more ISO 3166-1 alpha-2 country codes

all_videos = []

for country in countries:
    request = youtube.videos().list(
        part="snippet,statistics",
        chart="mostPopular",
        regionCode=country,
        videoCategoryId="10",  # Music
        maxResults=50
    )
    response = request.execute()
    
    for rank, item in enumerate(response["items"], start=1):
        all_videos.append({
            "rank": rank,
            "country": country,
            "title": item["snippet"]["title"],
            "channel": item["snippet"]["channelTitle"],
            "video_id": item["id"],
            "url": f"https://www.youtube.com/watch?v={item['id']}",
            "timestamp": datetime.utcnow().isoformat(),
            "source": "youtube"
        })

df = pd.DataFrame(all_videos)
df.to_csv("youtube_trending_by_country.csv", index=False)
print(df.head())
