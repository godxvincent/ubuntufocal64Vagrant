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

## Algunos comandos de trabajo sobre la terminal de la maquina.

`cp ~/repositorio/dags/* ~/airflow/dags/ -r | rm -rf ~/airflow/dags/__pycache__/`

## Questions I have regarding airflow.

- How I can set up my local environment to deploy my dags.
- How to run a diagram with an specific date?
