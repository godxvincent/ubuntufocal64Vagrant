from random import uniform
from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.task_group import TaskGroup


default_args = {"start_date": datetime(2020, 1, 1)}


def _training_model(task_instance):
    accuracy = uniform(0.1, 10.0)
    print(f"model's accuracy: {accuracy}")
    task_instance.xcom_push(key="model_accuracy", value=accuracy)


def _choose_best_model(task_instance):
    print("choose best model")
    accuracies = task_instance.xcom_pull(
        key="model_accuracy",
        task_ids=[
            "processing_tasks.training_model_a",
            "processing_tasks.training_model_b",
            "processing_tasks.training_model_c",
        ],
    )
    print("Este texto es de ayuda")
    print(accuracies)
    # Es posible retornar más de un id de una tarea para que sean ejecutadas,
    # solo basta con devolver un arreglo.
    if max(accuracies) > 8:
        return "accurate"

    return "inaccurate"


with DAG(
    "xcom_dag", schedule_interval="@daily", default_args=default_args, catchup=False
) as dag:

    #
    downloading_data = BashOperator(
        task_id="downloading_data", bash_command="sleep 3", do_xcom_push=False
    )

    with TaskGroup("processing_tasks") as processing_tasks:
        training_model_a = PythonOperator(
            task_id="training_model_a", python_callable=_training_model
        )

        training_model_b = PythonOperator(
            task_id="training_model_b", python_callable=_training_model
        )

        training_model_c = PythonOperator(
            task_id="training_model_c", python_callable=_training_model
        )

    choose_model = BranchPythonOperator(
        task_id="choose_model", python_callable=_choose_best_model
    )

    accurate = DummyOperator(task_id="accurate")
    inaccurate = DummyOperator(task_id="inaccurate")

    # https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/models/index.html#airflow.models.BaseOperator
    sorting = DummyOperator(task_id="sorting", trigger_rule="one_success")

    downloading_data.set_downstream(processing_tasks)
    processing_tasks.set_downstream(choose_model)
    choose_model.set_downstream([accurate, inaccurate])
    sorting.set_upstream([accurate, inaccurate])
