from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime, timedelta

# --- Funciones por módulo ---
from ingestion_1 import ingestion_air_quality_data
from ingestion_2 import ingestion_urbanization_data
from ingestion_3 import ingestion_population_data

from transform_1 import transform_air_quality_data
from transform_2 import transform_urbanization_data
from transform_3 import transform_population_data

from load_mongo import load_all_to_mongo, save_last_success_time

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="TechAndUrbanGrowth",
    default_args=default_args,
    description="ETL pipeline para datos de población, urbanización y calidad del aire",
    schedule_interval="@daily",
    catchup=False,
    tags=["etl", "mongodb", "worldbank", "openweather"]
) as dag:

    # --- Ingestión ---
    ingest_pop = PythonOperator(task_id="ingestion_population_data", python_callable=ingestion_population_data)
    ingest_urb = PythonOperator(task_id="ingestion_urbanization_data", python_callable=ingestion_urbanization_data)
    ingest_air = PythonOperator(task_id="ingestion_air_quality_data", python_callable=ingestion_air_quality_data)

    # --- Transformación ---
    transform_pop = PythonOperator(task_id="transform_population_data", python_callable=transform_population_data)
    transform_urb = PythonOperator(task_id="transform_urbanization_data", python_callable=transform_urbanization_data)
    transform_air = PythonOperator(task_id="transform_air_quality_data", python_callable=transform_air_quality_data)

    # --- Carga ---
    load_all = PythonOperator(task_id="load_all_to_mongo", python_callable=load_all_to_mongo)

    # --- Registro final ---
    save_success = PythonOperator(task_id="save_last_success_time", python_callable=save_last_success_time)
    final_step = DummyOperator(task_id="final_report_task")

    # --- Dependencias ---
    ingest_pop >> transform_pop
    ingest_urb >> transform_urb
    ingest_air >> transform_air

    [transform_pop, transform_urb, transform_air] >> load_all >> save_success >> final_step