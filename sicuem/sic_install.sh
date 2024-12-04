#!/usr/bin/bash

# Función para verificar la conexión a Internet
function check_internet() {
    while true; do
        ping -c 1 google.com &> /dev/null
        if [ $? -eq 0 ]; then
            echo "Hay conexión a Internet."
            break
        else
            echo "No hay conexión a Internet. Esperando..."
            sleep 5
        fi
    done
}

# Función para verificar/instalar si la biblioteca paho-mqtt está instalada
function install_paho() {
    python -c "import paho.mqtt.client" &> /dev/null
    if [ $? -eq 0 ]; then
        echo "La biblioteca paho-mqtt ya está instalada."
    else
        echo "La biblioteca paho-mqtt no está instalada. Instalando..."
        /usr/local/pyenv/versions/3.11.4/bin/python3 -m pip install paho-mqtt
    fi
}

function install_paramiko() {
    python -c "import paramiko" &> /dev/null
    if [ $? -eq 0 ]; then
        echo "La biblioteca paramiko ya está instalada."
    else
        echo "La biblioteca paramiko no está instalada. Instalando..."
        /usr/local/pyenv/versions/3.11.4/bin/python3 -m pip install paramiko
    fi
}


# Verifica la conexión a Internet
check_internet

# Verifica si la biblioteca paho-mqtt está instalada
install_paho
# Verifica si la biblioteca paramiko está instalada

install_paramiko
