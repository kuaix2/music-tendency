import os
from datetime import datetime
import pandas as pd
from googleapiclient.discovery import build

DATA_DIR = "/opt/airflow/data"  # default folder, can override

def fetch_youtube_trending(api_key: str, countries=None, category_id="10", data_dir=DATA_DIR, max_results=50) -> str:
    """
    Fetch YouTube trending videos for given countries and save as CSV.

    Args:
        api_key (str): YouTube API key
        countries (list): ISO 3166-1 alpha-2 country codes (default ["US"])
        category_id (str): YouTube video category (default "10" = Music)
        data_dir (str): Folder to save CSV
        max_results (int): Number of results per country

    Returns:
        str: Path to saved CSV
    """
    if countries is None:
        countries = ["US"]

    os.makedirs(data_dir, exist_ok=True)

    youtube = build("youtube", "v3", developerKey=api_key)
    all_videos = []

    for country in countries:
        request = youtube.videos().list(
            part="snippet,statistics",
            chart="mostPopular",
            regionCode=country,
            videoCategoryId=category_id,
            maxResults=max_results
        )
        response = request.execute()

        for rank, item in enumerate(response.get("items", []), start=1):
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
    filename = f"youtube_trending_{datetime.utcnow().strftime('%Y-%m-%d')}.csv"
    filepath = os.path.join(data_dir, filename)
    df.to_csv(filepath, index=False)
    print(f"Saved {filepath}")
    return filepath
