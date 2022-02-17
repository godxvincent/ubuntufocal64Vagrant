from contextlib import closing
import json

from airflow.models.baseoperator import BaseOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from elasticsearch_plugin.hooks.elastic_hook import ElasticHook


class PostgresToElasticOperator(BaseOperator):

    """
    Clase para crear un operador especializado
    """

    def __init__(
        self,
        sql,
        index,
        postgres_conn_id="postgres_elasticsearch",
        elastic_conn_id="elasticsearch_default",
        *args,
        **kwargs
    ) -> None:
        """
        Constructor para un operador especializado
        """
        super(PostgresToElasticOperator, self).__init__(*args, **kwargs)
        self.sql = sql
        self.index = index
        self.postgres_conn_id = postgres_conn_id
        self.elastic_conn_id = elastic_conn_id

    def execute(self, context):
        """
        Metodo para ejecutar la lógica para cargar la carga de postgres hacia
        elastic search
        """
        # Se de este print solo para que no salte el link
        # Falta validar en la documentación este context en que casos se usan.
        print(context)
        elastic_search_connection = ElasticHook(self.elastic_conn_id)
        postgres_connection = PostgresHook(postgres_conn_id=self.postgres_conn_id)
        with closing(postgres_connection.get_conn()) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.itersize = 1000
                cursor.execute(self.sql)
                for row in cursor:
                    doc = json.dumps(row, indent=2)
                    elastic_search_connection.add_doc(index=self.index, doc=doc)
