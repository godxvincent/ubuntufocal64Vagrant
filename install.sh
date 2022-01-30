#!/usr/bin/env bash

# ----------------------------------------------------------------------
# Este Script instala todos los paquetes necesarios para trabajar
# ----------------------------------------------------------------------

# Actualiza Aptitude
apt-get update

# Instala NodeJS el manejador de paquetes NPM
apt-get install -y nodejs
apt-get install -y npm

# Instala GIT
apt-get install -y git
