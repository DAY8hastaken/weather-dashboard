from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="weather_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule="*/1 * * * *",
    catchup=False,
    max_active_runs=1
) as dag:

    weather_task = BashOperator(
        task_id="run_weather_pipeline",
        bash_command="python /opt/airflow/dags/etl_weather.py"
    )