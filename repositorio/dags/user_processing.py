import json
from datetime import datetime
from pandas import json_normalize

from airflow.models import DAG
from airflow.providers.sqlite.operators.sqlite import SqliteOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

# Todas las tasks/operators will follow this parameters.
default_args = {"start_date": datetime(2022, 2, 1)}

CREATE_TABLE_QUERY = """
    CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY, 
        firstname TEXT NOT NULL,
        lastname TEXT NOT NULL,
        country TEXT NOT NULL,
        username TEXT NOT NULL, 
        password TEXT NOT NULL
    );
"""

FILE_PATH = "/tmp/processed_users.csv"
BASH_COMMAND = f"echo -e '.separator ','\n.import {FILE_PATH} users' | sqlite3 ~/airflow/airflow.db"


def _processing_users(ti):
    users = ti.xcom_pull(task_ids=["extracting_user"])
    print("Esto es lo que llega al pipeline")
    print(users)
    print("Fin del comunicado")
    if not len(users) or "results" not in users[0]:
        raise ValueError
    else:
        user = users[0]["results"][0]
        user_processed = json_normalize(
            {
                "firstname": user["name"]["first"],
                "lastname": user["name"]["last"],
                "country": user["location"]["country"],
                "username": user["login"]["username"],
                "password": user["login"]["password"],
                "email": user["email"],
            }
        )
        user_processed.to_csv(FILE_PATH, index=None, header=False)


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

    extracting_user = SimpleHttpOperator(
        task_id="extracting_user",
        http_conn_id="users_api",
        endpoint="api/",
        method="GET",
        response_filter=lambda response: json.loads(response.text),
        log_response=True,
    )

    processing_users = PythonOperator(
        task_id="processing_users", python_callable=_processing_users
    )

    storign_user = BashOperator(task_id="storing_user", bash_command=BASH_COMMAND)

    (
        creating_table
        >> is_api_available
        >> extracting_user
        >> processing_users
        >> storign_user
    )
