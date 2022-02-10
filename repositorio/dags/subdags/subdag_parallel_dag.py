from airflow.models import DAG
from airflow.operators.bash import BashOperator


def subdag_parallel_dag(parent_dag_id, child_dag_id, default_args):
    """
    Función para crear un subdag.
    param string parent_dag_id
    param string child_dag_id
    param dict default_args
    """
    sub_dag_id = f"{parent_dag_id}.{child_dag_id}"

    with DAG(
        dag_id=sub_dag_id,
        default_args=default_args,
    ) as dag:
        BashOperator(
            task_id="task_2",
            bash_command='sleep 3 | echo "task 2 executed"',
        )
        BashOperator(
            task_id="task_3",
            bash_command='sleep 3 | echo "task 3 executed"',
        )

        return dag
