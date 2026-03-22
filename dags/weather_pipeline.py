from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

from etl_weather import run_weather_pipeline
with DAG(
    dag_id="weather_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule="0 8 * * *",
    catchup=False,
    max_active_runs=1
) as dag:
    weather_task = PythonOperator(
        task_id="run_weather_pipeline",
        python_callable=run_weather_pipeline
    )