#!/usr/bin/env bash

# ----------------------------------------------------------------------
# Este Script instala todos los paquetes necesarios para trabajar
# ----------------------------------------------------------------------

# Actualiza Aptitude
apt update

# Instala NodeJS el manejador de paquetes NPM
apt install -y nodejs
apt install -y npm

# Instala GIT
apt install -y git
# Instala Python
apt install -y python3-pip 
# Instala Virtual Env
apt install -y python3.8-venv 
# Instala Postgres
apt install -y postgresql 

# Configuración del usuario de base de datos
# sudo -u postgres psql
# ALTER USER postgres PASSWORD 'postgres';
# instalar dentro del entorno virtual de apache airflow postgres
# Por lo que vi en esta instalación muchos de los requerimientos ya estan instalados.
# pip install 'apache-airflow[postgres]'

# Instalación de redis para usar celery
apt install -y redis
# Se debe configurar redis una vez instalado.
# sudo vim /etc/redis/redis.conf
# Aqui cambiamos el parametro supervised de no to systemd
# Se reinicia el servicio de redis 
# sudo systemctl restart redis.service
# Validar que redis si inicio sin problemas
# sudo systemctl status redis.service