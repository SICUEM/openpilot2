
# ![Logo de la Universidad Europea](https://upload.wikimedia.org/wikipedia/commons/3/3a/UE_Madrid_Logo_Positive_RGB.png)  
# SIC-PRUEBAS - Sunnypilot

**Rama de Desarrollo:** `sic-pruebas`  
**Proyecto Basado en:** Sunnypilot (fork de OpenPilot por Comma.ai)  
**Grupo de Investigación:** SICUEM

---

## 🧪 Descripción del Proyecto

La rama `sic-pruebas` es una extensión de Sunnypilot desarrollada por el grupo de investigación **SICUEM**, centrada en la mejora de sistemas avanzados de asistencia a la conducción (ADAS). En este proyecto, hemos trabajado en dos áreas clave:

- **Telemetría Avanzada:** Implementación de un sistema de telemetría que permite el monitoreo en tiempo real del estado del vehículo, recopilación de datos críticos y análisis del rendimiento del sistema.
  
- **Detección de Maniobras Críticas:** Desarrollo de algoritmos que permiten identificar cuándo el vehículo se aproxima a maniobras complejas, anticipándose a situaciones de riesgo para mejorar la seguridad.

Además, se han realizado mejoras significativas en la **interfaz de usuario (front-end)**, optimizando la visualización de datos relevantes y mejorando la experiencia de usuario.


## 📚 Documentación Adicional

Para más detalles técnicos, consulta la documentación completa del proyecto:  
👉 [Documentación del Proyecto](https://docs.google.com/document/d/1sxwJNi6hhJmm7Wsi8D8DlvUuuSTA4Juq6f6QMueI7lE/edit?usp=sharing)

---

## 👨‍💻 Integrantes del Proyecto

- **Adrián Cañadas**  
- **Javier Fernández**  
- **Nourdine Alaine**  
- **Sergio Bemposta**  

Grupo de Investigación **SICUEM** - Universidad Europea

---

## 🚀 Instalación y Configuración

### Requisitos Previos

- **Sistema Operativo:** Ubuntu 24.04 o superior
- **Dependencias:** Python 3.8+, C+, QT (para la interfaz gráfica)
- **Hardware:** Compatible con Comma Two o EON

### Clonación del Repositorio ---por hacer

Luego, clona el repositorio de manera parcial para una descarga más rápida:

git clone --filter=blob:none --recurse-submodules --also-filter-submodules https://github.com/commaai/openpilot.git

O realiza una clonación completa:

git clone --recurse-submodules https://github.com/commaai/openpilot.git

2. Configurar el Entorno

cd openpilot
tools/ubuntu_setup.sh

3. Sincronizar Git LFS

git lfs pull

4. Activar el Entorno Virtual de Python

source .venv/bin/activate

5. Compilar openpilot

scons -u -j$(nproc)

🏎️ Ejecución en Simulador

openpilot se puede ejecutar en simuladores como MetaDrive o CARLA mediante un puente de comunicación.
🚀 Iniciar openpilot

./tools/sim/launch_openpilot.sh

🔗 Uso del Bridge

./run_bridge.py -h

Esto mostrará las opciones disponibles:

usage: run_bridge.py [-h] [--joystick] [--high_quality] [--dual_camera] [--simulator SIMULATOR] [--town TOWN] [--spawn_point NUM_SELECTED_SPAWN_POINT] [--host HOST] [--port PORT]

Bridge between the simulator and openpilot.

options:
  -h, --help            show this help message and exit
  --joystick
  --high_quality
  --dual_camera
  --simulator SIMULATOR
  --town TOWN
  --spawn_point NUM_SELECTED_SPAWN_POINT
  --host HOST
  --port PORT

🚗 Ejecución en MetaDrive

Para iniciar el simulador MetaDrive con el bridge:

./run_bridge.py --simulator metadrive


