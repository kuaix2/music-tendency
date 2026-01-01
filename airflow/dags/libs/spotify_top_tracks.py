import os
import requests
import pandas as pd
from datetime import datetime
from base64 import b64encode

DATA_DIR = "/opt/airflow/data"  # default folder, can override

def get_spotify_token(client_id: str, client_secret: str) -> str:
    """Get OAuth token using Client Credentials flow."""
    auth_str = f"{client_id}:{client_secret}"
    b64_auth_str = b64encode(auth_str.encode()).decode()

    url = "https://accounts.spotify.com/api/token"
    headers = {"Authorization": f"Basic {b64_auth_str}"}
    data = {"grant_type": "client_credentials"}

    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def fetch_spotify_top_tracks_multi(client_id: str, client_secret: str,
                                   countries=None, data_dir: str = DATA_DIR,
                                   limit: int = 50) -> list:
    """
    Fetch Spotify top tracks for multiple countries and save CSVs.

    Args:
        client_id (str)
        client_secret (str)
        countries (list): ISO country codes (default ["US"])
        data_dir (str)
        limit (int): number of tracks per country

    Returns:
        list of saved CSV file paths
    """
    if countries is None:
        countries = ["US"]

    os.makedirs(data_dir, exist_ok=True)
    token = get_spotify_token(client_id, client_secret)
    saved_files = []

    # Spotify Top 50 playlists by country
    country_playlists = {
        "US": "37i9dQZEVXbLRQDuF5jeBp",
        "FR": "37i9dQZEVXbIPWwFssbupI",
        "GB": "37i9dQZEVXbLnolsZ8PSNw"
    }

    for country in countries:
        playlist_id = country_playlists.get(country, country_playlists["US"])
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        headers = {"Authorization": f"Bearer {token}"}
        params = {"limit": limit}

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        items = response.json().get("items", [])

        rows = []
        fetch_time = datetime.utcnow().isoformat()
        for idx, item in enumerate(items, start=1):
            track = item["track"]
            rows.append({
                "rank": idx,
                "country": country,
                "track_name": track["name"],
                "artist_name": ", ".join([a["name"] for a in track["artists"]]),
                "album_name": track["album"]["name"],
                "popularity": track["popularity"],
                "track_id": track["id"],
                "url": track["external_urls"]["spotify"],
                "timestamp": fetch_time,
                "source": "spotify"
            })

        df = pd.DataFrame(rows)
        filename = f"spotify_top_tracks_{country}_{datetime.utcnow().strftime('%Y-%m-%d')}.csv"
        filepath = os.path.join(data_dir, filename)
        df.to_csv(filepath, index=False)
        print(f"Saved {filepath}")
        saved_files.append(filepath)

    return saved_files
