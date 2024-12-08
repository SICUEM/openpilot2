#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
import time
import json
import signal
import sys
import os
from datetime import datetime
from threading import Thread, Event
from openpilot.common.params import Params
import cereal.messaging as messaging
import requests
import paho.mqtt.client as mqtt


class SicMqttHilo2:
  def __init__(self):
    self.initialize_variables()
    self.cargar_canales()
    self.initialize_mqtt_client()
    self.load_configuration()
    self.start_mqtt_thread()

  def initialize_variables(self):
    """
    Inicializa las variables principales de la clase.

    - Configura rutas de archivos JSON para canales y configuración.
    - Establece valores predeterminados para variables importantes como `espera` y `indice_canal`.
    - Inicializa eventos para pausar y detener hilos de forma segura.
    - Carga parámetros del sistema, como el `DongleID`, desde una base de datos interna.

    Comentarios clave:
    - `pause_event`: Permite pausar operaciones de manera segura.
    - `stop_event`: Señal para detener hilos en ejecución.
    """
    self.velocidadActualizacion=1
    self.jsonCanales = "../../sicuem/canales.json"  # Ruta al archivo JSON de configuración de canales
    self.jsonConfig = "../../sicuem/config.json"   # Ruta al archivo JSON de configuración general
    self.espera = 0.5                              # Intervalo de espera predeterminado en segundos
    self.indice_canal = 0                          # Índice inicial para los canales
    self.conectado = False

    self.sm = messaging.SubMaster(
      [ 'gpsLocationExternal'])


    # Estado inicial de conexión MQTT
    #self.sm = messaging.SubMaster(
     #     ['carState', 'controlsState', 'liveCalibration', 'carControl', 'gpsLocationExternal', 'gpsLocation',
      #     'navInstruction', 'radarState', 'drivingModelData'])                                 # Objeto SubMaster para recibir datos (sin inicializar)
    self.pause_event = Event()                     # Evento para pausar operaciones
    self.pause_event.set()                         # Activa el evento inicialmente
    self.stop_event = Event()                      # Evento para detener hilos
    params = Params()                              # Carga de parámetros del sistema
    self.params = params                           # Almacena la referencia a los parámetros
    self.DongleID = params.get("DongleId").decode('utf-8') if params.get("DongleId") else "DongleID"
    # El `DongleID` identifica de manera única el dispositivo conectado.

  def cargar_canales(self):
    """
    Carga la configuración de los canales desde el archivo JSON.
    - Utiliza `verificar_toggle_canales` para ajustar dinámicamente los canales habilitados/deshabilitados.
    - Filtra solo los canales habilitados (`enable: 1`).
    - Guarda las claves importantes asociadas a cada canal.
    """
    with open(self.jsonCanales, 'r') as f:
      data_canales = json.load(f)

    # Ajustar los canales habilitados/deshabilitados según los parámetros
    self.verificar_toggle_canales(data_canales)

    # Filtrar solo los canales habilitados
    self.enabled_items = [item for item in data_canales['canales'] if item['enable'] == 1]

    # Obtener los nombres de los canales habilitados para la suscripción
    self.lista_suscripciones = [item['canal'] for item in self.enabled_items]

    # Mapear claves importantes por canal
    self.keys_importantes_por_canal = {
      item['canal']: item.get('keys_importantes', [])
      for item in self.enabled_items
    }

  def initialize_mqtt_client(self):
    """
    Configura el cliente MQTT y sus callbacks.

    - Crea una instancia de cliente MQTT.
    - Asocia funciones de callback para manejar eventos de conexión, desconexión y recepción de mensajes.

    Comentarios clave:
    - `on_connect`: Se llama automáticamente cuando el cliente se conecta al broker.
    - `on_disconnect`: Maneja desconexiones, permitiendo reconexiones automáticas.
    - `on_message`: Procesa mensajes recibidos en los tópicos suscritos.
    """
    self.mqttc = mqtt.Client()                      # Inicializa el cliente MQTT
    self.mqttc.on_connect = self.on_connect         # Callback para manejar la conexión
    self.mqttc.on_disconnect = self.on_disconnect   # Callback para manejar la desconexión
    self.mqttc.on_message = self.on_message         # Callback para manejar mensajes recibidos


  def load_configuration(self):
    """
    Carga y procesa el archivo de configuración JSON.

    - Abre y lee el archivo de configuración general (`self.jsonConfig`).
    - Configura parámetros críticos como velocidad de envío, estado de pausa y dirección del broker MQTT.

    Manejo de errores:
    - Si el archivo no existe, está malformado o contiene claves no válidas, informa el error al usuario.
    - Cubre casos como valores no numéricos o divisiones por cero.

    Comentarios clave:
    - `self.espera`: Calcula el intervalo entre operaciones basado en la configuración de velocidad.
    - `self.pause_event`: Se limpia (desactiva) si el envío está deshabilitado (`send_value == 0`).
    """
    try:
        with open(self.jsonConfig, 'r') as f:
            self.dataConfig = json.load(f)  # Carga los datos desde el archivo JSON

        # Configuración de velocidad (tiempo de espera entre operaciones)
        speed_value = self.dataConfig['config']['speed']['value']
        self.espera = 1.0 / float(speed_value)

        # Configuración de envío (habilitar o deshabilitar operaciones)
        send_value = int(self.dataConfig['config']['send']['value'])
        if send_value == 0:
            self.pause_event.clear()  # Pausa las operaciones si `send` es 0

        # Dirección del broker MQTT
        self.broker_address = self.dataConfig['config']['IpServer']['value']

    except FileNotFoundError:
        print(f"Error: El archivo '{self.jsonConfig}' no se encontró.")
    except json.JSONDecodeError:
        print(f"Error: El archivo '{self.jsonConfig}' no contiene un JSON válido.")
    except KeyError as e:
        print(f"Error: Falta la clave {e} en la configuración del archivo JSON.")
    except ValueError as e:
        print(f"Error: Valor no válido en la configuración: {e}")
    except ZeroDivisionError:
        print("Error: La configuración de velocidad no puede ser cero.")
    except Exception as e:
        print(f"Error inesperado: {e}")


  def start_mqtt_thread(self):
    """
    Inicia un hilo no bloqueante para manejar la conexión MQTT.

    - Crea y lanza un hilo en segundo plano que ejecuta `setup_mqtt_connection`.
    - El hilo es "daemon", lo que significa que se detiene automáticamente cuando termina el programa.

    Comentarios clave:
    - Se usa un hilo para evitar que la conexión MQTT bloquee el flujo principal del programa.
    - `setup_mqtt_connection`: Se encarga de establecer la conexión con el broker y manejar reconexiones.
    """
    Thread(target=self.setup_mqtt_connection, daemon=True).start()




#----------------------------------------------------------------------------------------------- INIT STUFF END

  def start(self) -> int:
    #self.reanudar_envio() #


    self.cargar_canales()

    if self.lista_suscripciones:
      try:
        self.sm = messaging.SubMaster(
          ['carControl', 'gpsLocationExternal'])
      except Exception:
        self.sm = None



    time.sleep(self.velocidadActualizacion)
    hilo_telemetry = Thread(target=self.loop, daemon=True)
    hilo_telemetry.start()
    return 0


#------------------------------------------------------------------------------------------------ FUNCION START END

  def verificar_toggle_canales(self, data_canales):
    """
    Activa todos los canales sin importar el estado de los toggles.
    - Fuerza el atributo `enable` de cada canal a 1.
    - Imprime un mensaje para cada canal activado.
    """
    for item in data_canales['canales']:
      try:
        # Forzar el estado del canal a habilitado (enable = 1)
        if item['enable'] != 1:  # Solo actualiza si no está ya habilitado
          self.cambiar_enable_canal(item['canal'], 1)
          print(f"Canal habilitado: {item['canal']}")
      except Exception as e:
        print(f"Error al habilitar el canal {item['canal']}: {e}")

  def setup_mqtt_connection(self):
    """Configura la conexión MQTT y maneja los errores sin bloquear el programa."""
    while not self.stop_event.is_set():
      try:
        self.mqttc.connect(self.broker_address, 1883, 60)
        self.mqttc.subscribe("opmqttsender/messages", qos=0)
        self.mqttc.loop_start()
        self.conectado = True
        print("Conectado al broker MQTT con éxito.")
        break
      except Exception as e:
        print(f"Error al conectar con el broker MQTT: {e}")
        print("Reintentando conexión en 5 segundos...")
        time.sleep(5)  # Reintentar después de 5 segundos

  def signal_handler(self, sig, frame):
    """Manejador de la señal SIGINT para detener el programa de forma controlada."""
    self.cleanup()
    sys.exit(0)


#------------------------------------------------------------------------------------------------ VERIFICAR QUE TOGGLES ESTAN ACTIVADOS

  def loop(self):
    """
    Bucle principal que:
    - Verifica constantemente el estado de `telemetria_uem`.
    - Si `telemetria_uem` está habilitado (`True`), ejecuta `loop_principal`.
    - Si está deshabilitado (`False`), espera y sigue verificando.
    """
    self.conexion()  # Verifica la conexión a Internet en segundo plano

    # Hilo para publicar pings periódicos
    hilo_ping = Thread(target=self.loopPing, daemon=True)
    hilo_ping.start()

    while True:
      # Verificar el estado de telemetria_uem
      #if self.params.get_bool("telemetria_uem"):
        #print("Telemetría habilitada, ejecutando operaciones.")
      self.loop_principal()
      #else:
        #print("Telemetría deshabilitada, esperando...")

      time.sleep(0.5)  # Pausa breve antes de volver a verificar

  def loop_principal(self):
    """
    Ejecuta las operaciones principales de telemetría:
    - Carga dinámicamente los canales habilitados.
    - Envía datos importantes a través de MQTT.
    - Publica periódicamente el estado del archivo mapbox.
    """
    self.pause_event.wait()  # Pausa las operaciones si está desactivada la telemetría
    self.cargar_canales()  # Carga los canales habilitados dinámicamente

    if len(self.enabled_items) > 0 and self.sm:
      for canal_actual in self.enabled_items:
        canal_nombre = canal_actual['canal']
        if canal_nombre in self.sm.data:
          try:
            self.sm.update()
            # Convierte los datos de SubMaster a un diccionario
            datos_canal = self.sm[canal_nombre].to_dict()
            # Envía solo los datos importantes
            datos_importantes = self.enviar_datos_importantes(canal_nombre, datos_canal)
            self.mqttc.publish(
              str(canal_actual['topic']).format(self.DongleID),
              json.dumps(datos_importantes),
              qos=0
            )
          except KeyError:
            continue

    # Publicar estado del archivo mapbox
    self.enviar_estado_archivo_mapbox()

    # Espera configurada entre iteraciones
    time.sleep(self.espera)

  def loopPing(self):
    """Bucle que publica mensajes de ping periódicamente sin bloquear."""
    while not self.stop_event.is_set():
      self.pause_event.wait()
      self.mqttc.publish("telemetry_config/ping", str(time.time()), qos=0)
      time.sleep(3)

  ##------------------------------------------------------------------------------------------------ loop related end



  def on_connect(self, client, userdata, flags, rc):
    if rc == 0:
      self.conectado = True
      print("Conectado al broker MQTT con éxito.")

  def on_disconnect(self, client, userdata, rc):
    """Maneja la desconexión del cliente MQTT y trata de reconectar."""
    self.conectado = False
    print("Desconectado del broker MQTT. Intentando reconectar...")
    self.start_mqtt_thread()

  def on_message(self, client, userdata, msg):
    """
    Callback que maneja los mensajes recibidos en un tema MQTT.

    Parámetros:
    - client: Objeto del cliente MQTT.
    - userdata: Información del usuario asociada al cliente (generalmente None).
    - msg: Objeto que contiene el tema (`topic`) y el contenido del mensaje (`payload`).

    Comportamiento:
    - Si el mensaje se recibe en el tema "opmqttsender/messages":
        - Resetea los valores de todos los parámetros relacionados con direcciones (`sender_uem_*`) a `False`.
        - Activa únicamente el parámetro correspondiente basado en el contenido del mensaje.
    - Muestra el mensaje recibido por consola.

    Notas:
    - La función está optimizada para evitar múltiples condicionales utilizando un diccionario de mapeo.
    """
    if msg.topic == "opmqttsender/messages":
      message = msg.payload.decode()  # Decodifica el contenido del mensaje
      print(f"Mensaje recibido: {message}")  # Imprime el mensaje recibido

      # Resetea todos los parámetros relacionados con direcciones a False
      directions = ["sender_uem_up", "sender_uem_down", "sender_uem_left", "sender_uem_right"]
      for direction in directions:
        print()
        #
        #self.params.put_bool_nonblocking(direction, False)

      # Mapeo del mensaje a los parámetros correspondientes
      direction_map = {
        "up": "sender_uem_up",
        "down": "sender_uem_down",
        "left": "sender_uem_left",
        "right": "sender_uem_right"
      }

      # Activa el parámetro correspondiente si el mensaje es válido
      if message in direction_map:
        print()
        #
        #self.params.put_bool_nonblocking(direction_map[message], True)

  def cambiar_enable_canal(self, canal, estado):
    """
    Cambia el estado (`enable`) de un canal específico en el archivo JSON.

    Parámetros:
    - canal: Nombre del canal a modificar.
    - estado: Nuevo valor para el atributo `enable` (0 o 1).

    Comportamiento:
    - Lee el archivo JSON y busca el canal especificado.
    - Si el estado actual del canal es diferente del nuevo estado:
        - Actualiza el estado en memoria.
        - Guarda los cambios en el archivo JSON.
    - Si no hay cambios, evita reescribir el archivo.
    - Recarga los canales tras realizar un cambio.

    Notas:
    - La función es eficiente, ya que minimiza las escrituras al archivo JSON.
    """
    # Leer el archivo JSON
    with open(self.jsonCanales, 'r') as f:
      dataCanales = json.load(f)

    # Buscar el canal y verificar si requiere actualización
    canal_encontrado = False
    for item in dataCanales['canales']:
      if item['canal'] == canal:
        if item['enable'] != estado:  # Actualizar solo si es necesario
          item['enable'] = estado
          canal_encontrado = True
        break

    # Si el canal fue modificado, guardar los cambios
    if canal_encontrado:
      with open(self.jsonCanales, 'w') as f:
        json.dump(dataCanales, f, indent=4)
      print(f"Estado del canal '{canal}' cambiado a {estado}.")
      self.cargar_canales()  # Recargar los canales
    else:
      print(f"No se realizaron cambios para el canal '{canal}'.")

  def enviar_datos_importantes(self, canal, datos):
    """
    Filtra y envía solo los datos importantes para el canal dado.
    - Los campos relevantes se obtienen dinámicamente de `self.keys_importantes_por_canal`.
    """
    datos_importantes = {}

    # Obtener las claves importantes para este canal
    keys_importantes = self.keys_importantes_por_canal.get(canal, [])

    # Filtrar los datos relevantes
    for key in keys_importantes:
      if key in datos:
        datos_importantes[key] = datos[key]

    return datos_importantes


  def conexion(self, url='http://www.google.com', intervalo=5):
    """Verifica la conexión a Internet periódicamente en un hilo separado."""
    def check_connection():
      while not self.stop_event.is_set():
        try:
          response = requests.get(url, timeout=5)
          if response.status_code == 200:
            print("Conexión a Internet exitosa.")
        except requests.ConnectionError:
          print(f"No hay conexión a Internet. Intentando nuevamente en {intervalo} segundos...")
        time.sleep(intervalo)
    Thread(target=check_connection, daemon=True).start()

  def obtener_gps_location(self):
    # Crear una instancia del SubMaster para obtener datos del canal 'gpsLocationExternal'
    sm = self.sm

    # Actualizar para obtener los datos más recientes
    sm.update(0)

    # Verificar si el mensaje de gpsLocationExternal es válido
    latitude = sm['gpsLocationExternal'].latitude
    longitude = sm['gpsLocationExternal'].longitude
    altitude = sm['gpsLocationExternal'].altitude

    print("latitude", latitude)
    print("longitude", longitude)


    return {
      "latitude": latitude,
      "longitude": longitude,
      "altitude": altitude
    }

  def enviar_estado_archivo_mapbox(self):
    # Obtener la posición GPS actual desde el canal 'gpsLocationExternal'
    gps_data = self.obtener_gps_location()
    current_lat = gps_data.get('latitude')
    current_lon = gps_data.get('longitude')

    ruta_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_archivo = os.path.join(ruta_actual, "../system/manager/mapbox_response.json")

    if os.path.exists(ruta_archivo):
      try:
        with open(ruta_archivo, 'r') as archivo:
          data = json.load(archivo)
          closest_maneuvers = {
            "roundabout": {"distance": float('inf'), "latitude": None, "longitude": None},
            "intersection": {"distance": float('inf'), "latitude": None, "longitude": None},
            "merge": {"distance": float('inf'), "latitude": None, "longitude": None}
          }

          # Analizar las rutas y encontrar maniobras específicas
          if "routes" in data and len(data["routes"]) > 0:
            for leg in data["routes"][0].get("legs", []):
              for step in leg.get("steps", []):
                maneuver_type = step.get("maneuver", {}).get("type", "")
                maneuver_lat = step.get("maneuver", {}).get("location", [None, None])[1]
                maneuver_lon = step.get("maneuver", {}).get("location", [None, None])[0]

                if maneuver_type in closest_maneuvers:
                  # Calcular la distancia manualmente si las coordenadas son válidas
                  if current_lat is not None and current_lon is not None and maneuver_lat is not None and maneuver_lon is not None:
                    calculated_distance = self.calculate_distance(
                      current_lat, current_lon, maneuver_lat, maneuver_lon
                    )
                    if calculated_distance < closest_maneuvers[maneuver_type]["distance"]:
                      closest_maneuvers[maneuver_type] = {
                        "distance": calculated_distance,
                        "latitude": maneuver_lat,
                        "longitude": maneuver_lon
                      }

          roundabout_distance = closest_maneuvers["roundabout"]["distance"]
          intersection_distance = closest_maneuvers["intersection"]["distance"]
          merge_distance = closest_maneuvers["merge"]["distance"]

          # Convertir los valores flotantes a cadenas antes de almacenarlos
          self.params.put("roundabout_distance", str(roundabout_distance))
          self.params.put("intersection_distance", str(intersection_distance))
          self.params.put("merge_distance", str(merge_distance))

          # Procesar distancias, reemplazando valores no válidos con -1
          distances = {
            "roundabout": roundabout_distance if roundabout_distance != float('inf') else -1,
            "intersection": intersection_distance if intersection_distance != float('inf') else -1,
            "merge": merge_distance if merge_distance != float('inf') else -1,
          }

          # Cambiar nombre de la maniobra si está a menos de 2 metros
          for maneuver, distance in distances.items():
            if 0 <= distance < 2:  # La distancia es válida y menor a 2 metros
              distances[f"{maneuver}_hecha"] = distances.pop(maneuver)  # Cambiar el nombre de la maniobra
              print(f"Maniobra completada: {maneuver}")

          # Filtrar distancias válidas para publicación
          valid_distances = {key: value for key, value in distances.items() if value >= 0 and "_hecha" not in key}

          # Preparar el contenido para MQTT
          contenido = (
            f"Roundabout distance: {distances.get('roundabout', -1)} m\n"
            f"Intersection distance: {distances.get('intersection', -1)} m\n"
            f"Merge distance: {distances.get('merge', -1)} m"
          )
          print(f"Distancias enviadas: {distances}")
          self.mqttc.publish("telemetry_mqtt/mapbox_status", contenido, qos=0)


      except Exception as e:
        print(f"Error al procesar el archivo Mapbox: {e}")
    else:
      self.params.put("roundabout_distance", "-1")
      self.params.put("intersection_distance", "-1")
      self.params.put("merge_distance", "-1")
      print("Archivo Mapbox no encontrado. Todas las distancias configuradas a -1.")

  def calculate_distance(self, lat1, lon1, lat2, lon2):
    """Calcula la distancia entre dos puntos geográficos usando la fórmula de Haversine."""
    if None in [lat1, lon1, lat2, lon2]:
      return float('inf')

    # Conversión de coordenadas a radianes
    lat1, lon1, lat2, lon2 = map(lambda x: x * (math.pi / 180), [lat1, lon1, lat2, lon2])

    # Fórmula de Haversine
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    R = 6371000  # Radio de la Tierra en metros
    return R * c




