from datetime import datetime

from airflow.models import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.subdag import SubDagOperator
from subdags.subdag_parallel_dag import subdag_parallel_dag

default_args = {"start_date": datetime(2022, 2, 1)}
MAIN_DAG = "parallel_dag"

with DAG(
    MAIN_DAG,
    schedule_interval="@daily",
    default_args=default_args,
    catchup=False,
) as dag:
    task_1 = BashOperator(
        task_id="task_1",
        bash_command='sleep 3 | echo "task 1 executed"',
    )

    SUBDAG_PROCESSING = "processing_tasks"
    processing = SubDagOperator(
        task_id=SUBDAG_PROCESSING,
        subdag=subdag_parallel_dag(
            MAIN_DAG, SUBDAG_PROCESSING, default_args=default_args
        ),
    )

    task_4 = BashOperator(
        task_id="task_4",
        bash_command='sleep 3 | echo "task 4 executed"',
    )

    task_1.set_downstream(processing)
    task_4.set_upstream(processing)
