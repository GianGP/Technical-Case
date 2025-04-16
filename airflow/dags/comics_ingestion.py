# Importing necessary modules
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.sensors.python import PythonSensor
from airflow.models import Variable
import requests
import logging

# Default arguments applied to all tasks in the DAG
default_args = {
    'owner': 'giangp',
    'depends_on_past': False,
    'start_date': datetime(2025, 4, 10),
    'email': ['your@email.com'],
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'max_active_runs': 1,
    'catchup': False
}


# Calculate next comic number
def get_next_comic_number(**context):
    ti = context['ti']

    # Retrieve last comic number queried and add 1
    comic_number = int(Variable.get("comic_number", default_var=0)) + 1
    
    # Log current comic number
    logging.info(f'Current comic number: {comic_number}')
    
    # Save current comic number
    ti.xcom_push(key='comic_number', value=comic_number)

# Builds comics url
def build_dynamic_endpoint(**context):
    ti = context['ti']
    
    # Retrieve current comic number
    comic_number = ti.xcom_pull(task_ids='calculate_next_comic_number', key='comic_number')

    # Build endpoint
    endpoint = f"/{comic_number}/info.0.json"

    # Log endpoint
    logging.info(f"Current endpoint: {endpoint}")

    # Save current endpoint
    ti.xcom_push(key='endpoint', value=endpoint)

# Checks if endpoint is available
def api_poll(**context):
    ti = context['ti']

    # Retrieve current comic number
    comic_number = ti.xcom_pull(task_ids='calculate_next_comic_number', key='comic_number')

    # Build endpoint
    url = f"https://xkcd.com/{comic_number}/info.0.json"

    # Log current endpoint
    logging.info(f"Checking URL: {url}")

    # Call endpoint and return if it is available or not to python sensor
    response = requests.get(url)
    return response.status_code == 200

# Retrieves API data
def get_comic_data(**context):
    ti = context['ti']
    
    # Retrieve current comic number
    comic_number = ti.xcom_pull(task_ids='calculate_next_comic_number', key='comic_number')
    
    # Build endpoint
    url = f"https://xkcd.com/{comic_number}/info.0.json"
    
    # Log endpoint
    logging.info(f"Calling URL: {url}")

    # Call endpoint, log and store response
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    logging.info(f"API result: {data}")

    # Save API response
    ti.xcom_push(key='comic_data', value=data)

# Set new comic number value
def set_current_comic_number(**context):
    ti = context['ti']
    
    # Retrieve current comic number
    current_number = ti.xcom_pull(task_ids='calculate_next_comic_number', key='comic_number')

    # Save current executed comic number
    Variable.set('comic_number', current_number)
    logging.info(f'Latest comic number saved: {current_number}')


# DAG definition
with DAG(
    dag_id='ingest_comic_data_to_db',
    default_args=default_args,
    schedule_interval='0 6 * * 1,3,5',
    description='Polls API and loads data to Postgres',
) as dag:

    # Calculate new id
    retrieve_comic_number = PythonOperator(
        task_id='calculate_next_comic_number',
        python_callable=get_next_comic_number
    )

    # Use sensor to poll comics API
    wait_for_api = PythonSensor(
        task_id='wait_comic_to_be_available',
        python_callable=api_poll,
        poke_interval=60,
        timeout=300,
        mode='poke',
    )

    # Retrieve data from API
    get_data = PythonOperator(
        task_id='get_comic_data',
        python_callable=get_comic_data
    )

    # Create table if it's not available
    create_table = SQLExecuteQueryOperator(
        task_id='create_table',
        conn_id='postgres_default',
        sql="""
        CREATE TABLE IF NOT EXISTS raw_data (
            id SERIAL PRIMARY KEY,
            data JSONB NOT NULL,
            processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
        """
    )

    # Insert data into PostgreSQL
    insert_data = SQLExecuteQueryOperator(
        task_id='insert_data',
        conn_id='postgres_default',
        sql="""
        INSERT INTO raw_data (data)
        VALUES (%(comic_data)s)
        ON CONFLICT (id) DO UPDATE SET
            data = EXCLUDED.data,
            processed_at = NOW()
        """,
        parameters={
            'comic_data': "{{ ti.xcom_pull(task_ids='get_comic_data', key='comic_data') | tojson }}"
        }
    )

    # Update latest comic book number
    update_variable = PythonOperator(
        task_id='update_variable',
        python_callable=set_current_comic_number
    )

    # Set execution order
    retrieve_comic_number >> wait_for_api >> get_data >> create_table >> insert_data >> update_variable