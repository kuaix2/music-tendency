from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

with DAG(
    dag_id="hello_world_dag_1min",
    start_date=datetime(2025, 12, 24),
    schedule_interval=timedelta(minutes=1),  # runs every minute
    catchup=False,
) as dag:

    say_hello = BashOperator(
        task_id="say_hello",
        bash_command="echo 'Hello Airflow!'"
    )
