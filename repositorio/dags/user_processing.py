from airflow.models import DAG
from datetime import datetime

# Todas las tasks/operators will follow this parameters.
default_args = {
     "start_date":datetime(2020, 1, 1)
}

# run once everyday
with DAG("user_processing", schedule_interval="@daily", catchup=False) as dag:
    # define tasks/operator
    pass

