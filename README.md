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

* Instalación de airflow


```pip install "apache-airflow[celery]==2.2.3" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.2.3/constraints-3.8.txt"```

* Iniciar los archivos base de configuración de airflow (ejecutese solo la primera vez)

`airflow init db`

* Iniciar el servidor web

`airflow webserver`

* Crear usuario administrador

`airflow users create -u admin -f Ricardo -l Vargas -r Admin -e godxvincent@gmail.com`

**Otros comandos utiles**

* subir versión archivos inicializacion.

`airflow db upgrade`

* Re inicia la configuración de airflow (resetea toda la metadata)

`airflow db reset`

* Encargado de agendar los data pipelines de las tareas.
`airflow scheduler`

* Listar todos los dags que hay (en este caso los de ejemplo que trae)
`airflow dags list`

## Conceptos de airflow
### Tipos de operadores
> `Action Operators:` Corresponde a operadores que ejecutan una **acción/función.**
>
> * Python Operators
> * Bash Operators 
>
> `Transfer Operators:` Corresponde a operadores que **mueven** información de una fuente a un destino.
>
> `Sensor Operators:` Corresponde a operadores que **esperan** para que una condición se de.