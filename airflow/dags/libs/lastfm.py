import os
from datetime import datetime
import requests
import pandas as pd

DATA_DIR = "/opt/airflow/data"  # default, can override

def fetch_lastfm_top_tracks(api_key: str, data_dir: str = DATA_DIR, limit: int = 100) -> str:
    """
    Fetch Last.fm top tracks and save as CSV.
    
    Returns the filepath of the saved CSV.
    """
    os.makedirs(data_dir, exist_ok=True)
    
    URL = "https://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "chart.gettoptracks",
        "api_key": api_key,
        "format": "json",
        "limit": limit
    }
    
    response = requests.get(URL, params=params)
    response.raise_for_status()
    data = response.json()

    tracks = data["tracks"]["track"]
    fetch_date = datetime.utcnow()

    rows = []
    for t in tracks:
        rows.append({
            "track": t["name"],
            "artist": t["artist"]["name"],
            "playcount": int(t["playcount"]),
            "listeners": int(t["listeners"]),
            "mbid": t.get("mbid"),
            "date_fetched": fetch_date
        })

    df = pd.DataFrame(rows)
    filename = f"lastfm_top_tracks_{fetch_date.strftime('%Y-%m-%d')}.csv"
    filepath = os.path.join(data_dir, filename)
    df.to_csv(filepath, index=False)
    print(f"Saved {filepath}")
    return filepath
