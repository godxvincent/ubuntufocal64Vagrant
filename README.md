# UbuntuFocal64-VagrantPlugins

[![vagrant](https://img.shields.io/badge/vagrant-v2.2.19-blue.svg?style=plastic&logo=Vagrant&logoColor=blue)](https://www.vagrantup.com/)
[![virtualbox](https://img.shields.io/badge/virtualbox-v6.1.32-red.svg?style=plastic&logo=VirtualBox)](https://www.virtualbox.org/wiki/VirtualBox)

Este repositorio contiene código de base para levantar una maquina virtual en vagrant. Espero poder convertirlo en un template para no tener que lidiar con todas las configuraciones y cosas de base.

Iniciar imagen
`vagrant up`

Conectarse a la maquina via ssh.
`vagrant ssh`

Destruir la maquina
`vagrant destroy`

## Comandos para instalar y configurar airflow.

**Comandos de la instalación inicial**

- Instalación de airflow

  `pip install "apache-airflow[celery]==2.2.3" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.2.3/constraints-3.8.txt"`

- Iniciar los archivos base de configuración de airflow (ejecutese solo la primera vez)

  `airflow init db`

- Iniciar el servidor web

  `airflow webserver`

- Crear usuario administrador

  `airflow users create -u admin -f Ricardo -l Vargas -r Admin -e godxvincent@gmail.com`

**Comandos para usar celery executors**

- inicializar flower (esto es una herramienta para monitorear el estado de los workers)

  `airflow celery flower`

- Registrar un nodo como worker (esto debe hacerse en las maquinas remotas que hacen parte del cluster aunque puede hacerse en la maquina local para registrarla.)

  `airflow celery worker`

**Otros comandos utiles**

- subir versión archivos inicializacion.

  `airflow db upgrade`

- Re inicia la configuración de airflow (resetea toda la metadata)

  `airflow db reset`

- Encargado de agendar los data pipelines de las tareas.

  `airflow scheduler`

- Listar todos los dags que hay (en este caso los de ejemplo que trae)

  `airflow dags list`

- Probando localmente que el test esta funcionando correctamente.

  `airflow tasks test (name_dag) (name_task) (start_date)`
  `airflow tasks test user_processing creating_table 2022-02-04`

- Listar todos los providers instalados

  `airflow providers list`

- validar configuración de airflow.

  `airflow config get-value core parameter`

  `airflow config get-value core sql_alchemy_conn` Permite saber la base de datos de airflow (si es sqlite no permite ejecuciones en paralelo)

  `> sqlite:////home/vagrant/airflow/airflow.db`

  `airflow config get-value core executor` Permite saber como estan configurados los ejecutores de airflow.

  `> SequentialExecutor`

- Validar que haya conexión a la base de datos

  `airflow db check`

## Conceptos de airflow

### Tipos de operadores

> `Action Operators:` Corresponde a operadores que ejecutan una **acción/función.**
>
> - Python Operators
> - Bash Operators
>
> `Transfer Operators:` Corresponde a operadores que **mueven** información de una fuente a un destino.
>
> `Sensor Operators:` Corresponde a operadores que **esperan** para que una condición se de.

### Backfilling and Catchup

> `Catchup:` Es una funcionalidad de airflow que busca ejecutar todos los DAGs desde la fecha de inicio hasta la fecha actual (en paralelo) con el fin de ponerse al día con las ejecuciones (skipped). Esto es controlado con el parametro catchup al definir el dag. Pero adicionalmente, airflow tiene en consideración para ponerse al día cual fue la última fecha de ejecución en adelante.

```python
with DAG(
    "user_processing",
    schedule_interval="@daily",
    default_args=default_args,
    catchup=False, # Este parametro permite definir si el DAG tendrá habilitada la funcionalidad de catchup
) as dag:
```

### Orden de ejecución

> Aun con tareas dispuestas en paralelo airflow las ejecuta por default en paralelo, esto se debe a que airflow requiere para ambientes productivos una configuración especial. Cambiar el tipo de executor y la conexión a base de datos que debe ser postgres o mysql (se sugiere postgres).

Adicionalmente se requiere de lo siguiente:

- Configurar un message broker (redis, rabbit mq)

### Parametros para controlar los distintos paralelismos de airflow.

Estos parametros pueden ser encontrados en el archivo `~/airflow/airflow.cfg`

- **parallelism:** Controla el numero total de tareas que puedes ejecutar al mismo tiempo en todo tu sistema de airflow.

- **max_active_tasks_per_dag** Controla el numero permitido de instancias de tareas corriendo concurrentemente para un DAG. Segun el curso antes el parametro se llamaba **dag_concurrency**. Este comportamiento también puede ser seteado en la definición del DAG.

```python
with DAG(
    "parallel_dag",
    schedule_interval="@daily",
    default_args=default_args,
    catchup=False,
    max_active_tasks = 2 # De esta manera se puede setear cuantas tareas activas por dag se pueden ejecutar en este dag.
) as dag:
```

- **max_active_runs_per_dag** Controla el número maximo de dags que pueden estar corriendo en paralelo.

### SubDags

Los subdags son dags que son ejecutados desde uno de nivel superior. No se recomiendan por que por default esos son ejecutados de forma secuencial (sequential executor), incluso si se establece que el tipo de executore es uno distinto.

### XCOM

Obedece a la sigla de Cross Communication y basicamente es una forma de intercambiar pequeñas cantidades de datos entre tasks. La información a intercambiar se guarda como parte de la metadata en la base de datos de airflow. Lo anterior significa que hay limitaciones de almacenadmiento los cuales se listan a continuación

- sqlite = 2gb
- postgres = 1gb
- mysql = 64Kb

Por default cuando una función (o en el caso de los operadores de python), en la base de datos queda guardado con un identificador que siempre será `return_value`. Sin embargo si se quiere enviar un valor usando un identificador propio se debe hacer uso de la función `xcom_push`

```python
# Esto hace que retorne un valor y sea legible como un Xcom pero queda guardado como un return_value
def _training_model():
    accuracy = uniform(0.1, 10.0)
    print(f"model's accuracy: {accuracy}")
    return accuracy

# De esta otra manera se puede especificar el valor de la llave con el que se desea guardar la información.
def _training_model(task_instance):
    accuracy = uniform(0.1, 10.0)
    print(f"model's accuracy: {accuracy}")
    task_instance.xcom_push(key="model_accuracy", value=accuracy)
```

Para recuperar el valor se hace uso de la variable de task_instance y se ejecuta el metodo xcom_pull el cual recibe dos parametros el id de la llave a buscar y el listado de tareas de las cuales se espera recuperar la información.

```python
def _choose_best_model(task_instance):
    print("choose best model")
    accuracies = task_instance.xcom_pull(
        key="model_accuracy",
        task_ids=[
            "processing_tasks.training_model_a"
            "processing_tasks.training_model_b"
            "processing_tasks.training_model_c"
        ],
    )
    print(accuracies)
```

El parametro `do_xcom_push` de la mayoría de operadores permite configurar si una task dejará en el xcom alguna salida, por default siempre deja algo.

```python
downloading_data = BashOperator(
        task_id="downloading_data", bash_command="sleep 3", do_xcom_push=False
    )
```

**(Documentación de Airflow)** Clases de Airflow

- [BaseOperator](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/models/index.html#airflow.models.BaseOperator)
- [BashOperator](https://airflow.apache.org/docs/apache-airflow/stable/_modules/airflow/operators/bash.html#BashOperator)

### Plugins

Plugins son una forma de customizar o crear operadores propios. También es posible agregar views a las instancias de airflow, basicamente se pueden agregar vistas de controles externos. Para interactuar con soluciones de terceros (third party tool) se hace uso de los hooks.

Para configurar los plugins se debe copiar el codigo del plugin en la carpeta `~/airflow/plugins`.

Para crear un plugin hay que crear una clase que herede de la clase `AirflowPluginClass` y dentro de esa clase se incluyen las vistas, hooks y operators en si mismo (Esto hasta la antes de la versión 2.0 de airflow).
En las versiones recientes la clase `AirflowPluginClass` solo se usa para personalizar las vistas. Y en cuanto a los hooks y operadores solo se deben crear los modules en python dentro del folder y ya esta.

Los plugin son de naturaleza lazy, esto significa que cada que se carga un plugin se debe reiniciar la instancia de AirFlow (aunque esto se puede ajustar con un parametros en la configuración)

Guia de como generar un hook, si o si es necesario crear la clase.
https://airflow.apache.org/docs/apache-airflow/2.2.3/plugins.html#interface

## Algunos comandos de trabajo sobre la terminal de la maquina.

`cp ~/repositorio/dags/* ~/airflow/dags/ -r | rm -rf ~/airflow/dags/__pycache__/`
`cp ~/repositorio/plugins/* ~/airflow/plugins/ -r | rm -rf ~/airflow/plugins/__pycache__/`

La palabra `connection` es el nombre del indice en el que se desea hacer la busqueda.

`curl -X GET 'http://localhost:9200/connection/\_search' -H "Content-type: application/json" -d '{"query":{"match_all":{}}}'`

## Questions I have regarding airflow.

- How I can set up my local environment to deploy my dags.
- How to run a diagram with an specific date?
- How can I see the subdag without run the main dag?
- There's a way to see how a dag was during a moment!? I mean, the dag had a shape and then and updating was done, can I see in airflow console how was my dag before the update?
