# This is the class you derive to create a plugin
from airflow.plugins_manager import AirflowPlugin
from airflow.hooks.base import BaseHook
from elasticsearch import Elasticsearch


class ElasticHook(BaseHook):
    """This is a class for a elastick search hook"""

    def __init__(self, conn_id="elasticsearch_default", *args, **kwargs):
        super().__init__(*args, **kwargs)
        conn = self.get_connection(conn_id)
        print("Impresión variable conn")
        print(conn)
        conn_config = {}
        hosts = []

        if conn.host:
            print("Se ha conectado correctamente")
            print(conn.host)
            hosts.append("http://localhost:9200")

        # if conn.port:
        #     conn_config["port"] = int(conn.port)

        if conn.login:
            # Este password podria no venir solo si es requerido.
            conn_config["http_auth"] = (conn.login, conn.password)

        self.es = Elasticsearch(hosts, **conn_config)
        self.index = conn.schema

    def info(self):
        """
        función para mostrar la informaciónd de elastic search
        """
        self.es.info()

    def set_index(self, index):
        """
        función para definir el indice que se va a utilizar
        """
        self.index = index

    def add_doc(self, index, doc):
        """
        función para adicionar un documento en un indice.
        """
        self.set_index(index)
        result = self.es.index(index=index, document=doc)
        return result


# Defining the plugin class
class AirflowTestPlugin(AirflowPlugin):

    """
    Clase para importar los hooks, views, macros y otros
    """

    name = "test_plugin"
    hooks = [ElasticHook]
    macros = []
    flask_blueprints = []
    appbuilder_views = []
    appbuilder_menu_items = []
    global_operator_extra_links = []
    operator_extra_links = []
