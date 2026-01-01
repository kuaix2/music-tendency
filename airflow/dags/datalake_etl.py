from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime, timedelta
from libs.lastfm import fetch_lastfm_top_tracks
from libs.youtube_trending import fetch_youtube_trending

LASTFM_API_KEY = "e7aba3723288199ad3e3769c17ca6e86"
YOUTUBE_API_KEY = "AIzaSyAVCxOYVwFPP8EruwXP9FY4K8oqgqGPCJA"

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    dag_id='datalake_daily_fetch',
    default_args=default_args,
    description='Fetch Last.fm and YouTube trending data daily and convert to Parquet',
    schedule_interval="@daily",
    start_date=datetime(2025, 12, 24),
    catchup=False
) as dag:

    # ----------------------------
    # Fetch tasks
    # ----------------------------
    fetch_lastfm_task = PythonOperator(
        task_id='fetch_lastfm',
        python_callable=fetch_lastfm_top_tracks,
        op_kwargs={'api_key': LASTFM_API_KEY}
    )

    fetch_youtube_task = PythonOperator(
        task_id='fetch_youtube',
        python_callable=fetch_youtube_trending,
        op_kwargs={'api_key': YOUTUBE_API_KEY, 'countries': ["US","FR","GB"]}
    )

    # ----------------------------
    # Optional formatting / cleaning tasks
    # ----------------------------
    format_lastfm_task = PythonOperator(
        task_id='format_lastfm',
        python_callable=lambda: print("Formatting Last.fm CSV for Spark")
    )

    format_youtube_task = PythonOperator(
        task_id='format_youtube',
        python_callable=lambda: print("Formatting YouTube CSV for Spark")
    )

    # ----------------------------
    # Spark CSV -> Parquet task
    # ----------------------------
    csv_to_parquet_task = SparkSubmitOperator(
        task_id="csv_to_parquet",
        application="/opt/spark/jobs/csv_to_parquet.py",
        conn_id="spark_default",  # Uses the connection you created in UI
        verbose=True,
        # Add these parameters to be explicit and avoid any YARN issues
        deploy_mode='client',
        driver_memory='1g',
        executor_memory='2g',
        executor_cores=1,
        num_executors=1,
    )

    # ----------------------------
    # Set dependencies
    # ----------------------------
    fetch_lastfm_task >> format_lastfm_task
    fetch_youtube_task >> format_youtube_task

    format_lastfm_task >> csv_to_parquet_task
    format_youtube_task >> csv_to_parquet_task