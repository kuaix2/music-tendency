from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import pandas as pd
import os

# --------------------
# Config
# --------------------
API_KEY = "e7aba3723288199ad3e3769c17ca6e86"
URL = "https://ws.audioscrobbler.com/2.0/"
DATA_DIR = "/opt/airflow/data"  # adjust to your data folder
os.makedirs(DATA_DIR, exist_ok=True)

# --------------------
# Python function to fetch and save CSV
# --------------------
def fetch_lastfm_top_tracks():
    params = {
        "method": "chart.gettoptracks",
        "api_key": API_KEY,
        "format": "json",
        "limit": 100
    }

    response = requests.get(URL, params=params)
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
    filepath = os.path.join(DATA_DIR, filename)
    df.to_csv(filepath, index=False)
    print(f"Saved {filepath}")

# --------------------
# DAG definition
# --------------------
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    dag_id='lastfm_top_tracks_daily',
    default_args=default_args,
    description='Fetch Last.fm top tracks daily',
    schedule_interval=timedelta(minutes=1),
    start_date=datetime(2025, 12, 24),
    catchup=False
) as dag:

    fetch_task = PythonOperator(
        task_id='fetch_lastfm_data',
        python_callable=fetch_lastfm_top_tracks
    )

fetch_task
