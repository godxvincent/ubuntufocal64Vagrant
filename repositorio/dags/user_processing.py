from datetime import datetime

from airflow.models import DAG
from airflow.providers.sqlite.operators.sqlite import SqliteOperator
from airflow.providers.http.sensors.http import HttpSensor

# Todas las tasks/operators will follow this parameters.
default_args = {"start_date": datetime(2020, 1, 1)}

CREATE_TABLE_QUERY = """
    CREATE TABLE users (
        email TEXT PRIMARY KEY, 
        firstname TEXT NOT NULL,
        lastname TEXT NOT NULL,
        country TEXT NOT NULL,
        username TEXT NOT NULL, 
        password TEXT NOT NULL
    );
"""

# run once everyday
with DAG(
    "user_processing",
    schedule_interval="@daily",
    default_args=default_args,
    catchup=False,
) as dag:
    # define tasks/operator
    creating_table = SqliteOperator(
        task_id="creating_table", sqlite_conn_id="db_sqlite", sql=CREATE_TABLE_QUERY
    )

    is_api_available = HttpSensor(
        task_id="is_api_available", http_conn_id="users_api", endpoint="api/"
    )
